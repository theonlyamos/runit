import os
import sys
import json
import time
import shelve
import getpass
import asyncio
import logging
import argparse
import websockets
from pathlib import Path
from typing import Type, Optional
from threading import Thread


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values

from .languages import LanguageParser
from .modules import Account
from .runit import RunIt
from .constants import (
    VERSION, CURRENT_PROJECT, CURRENT_PROJECT_DIR,
    EXT_TO_RUNTIME, LANGUAGE_TO_RUNTIME, RUNIT_HOMEDIR,
    SERVER_HOST, SERVER_PORT, CONFIG_FILE
)
from .exceptions import (
    ProjectExistsError,
    ProjectNameNotSpecified
)
from .core import WebServer

      
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('runit.log')
logging.getLogger('urllib3').setLevel(logging.WARNING)

load_dotenv()

# eventlet.monkey_patch()

def start_webserver(project: RunIt, host: str = SERVER_HOST, port: int = SERVER_PORT):
    web_server = WebServer(project)
    web_server.start(host, port)

async def start_websocket(project: RunIt):
    url = os.getenv('RUNIT_API_ENDPOINT')
    if not url:
        raise Exception('set RUNIT_API_ENDPOINT environment variable')

    url = url.replace('/api/', '/')
    
    client_id = int(time.time())

    uri: str = url.replace('http', 'ws') + 'ws/' + str(client_id)

    async with websockets.connect(uri) as websocket:
        logger.info(f"Serving on {url}e/{client_id}")
        await websocket.send(json.dumps({"type": "client"}))
        # Wait for incoming messages
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                if "message" in list(data.keys()):
                    print(f"Received message from server: {data['message']}", flush=True)
                else:
                    logger.info(f"Accessing function: {data['function']} with paramters: {data['parameters']}")
                    response = {'type': 'response', 'data': project.serve(data['function'], data['parameters'])}
                    await websocket.send(json.dumps(response))
            except websockets.exceptions.ConnectionClosed:
                print("Connection with server closed")
                break
    
    # @socket.event
    # async def connect():
    #     await socket.emit('handshake', {'type': 'client'})
        
    # @socket.event
    # async def disconnect():
    #     logger.info('Disconnected Websocket')

    # @socket.event
    # async def handshake(data):
    #     logger.info(f"Serving on {url}e/{data}")

    # @socket.event
    # async def connect_error(error):
    #     logger.warn(error)
    #     logger.info('Websocket Error')

    # @socket.event
    # async def exposed(data):
    #     logger.info(f"Accessing function: {data['function']} with paramters: {data['parameters']}")
    #     await socket.emit('expose', project.serve(data['function'], data['parameters']))

    # await socket.connect(url, transports=['websocket'])
    # await socket.wait()

def create_config(args):
    config = {}
    config['name'] = args.name
    config['language'] = args.language
    config['runtime'] = args.runtime if args.runtime else LANGUAGE_TO_RUNTIME[args.language]
    config['private'] = args.private
    config['author'] = {}
    config['author']['name'] = getpass.getuser()
    config['author']['email'] = "name@example.com"
    
    user = Account.user()
    # print(user)
    os.chdir(CURRENT_PROJECT_DIR)
    if len(user.keys()):
        config['author']['name'] = user['name']
        config['author']['email'] = user['email']
    
    return config

def create_project(config):
    return RunIt(**config)

def create_new_project(args):
    global CURRENT_PROJECT
    '''
    Method for creating new project or
    function from command line arguments

    @param args Arguments from argparse
    @return None
    '''
    try:
        if args.name:
            name = RunIt.set_project_name(args.name)
            if RunIt.exists(name):
                raise ProjectExistsError(f'{name} project already exists')

            config = create_config(args)
            CURRENT_PROJECT = create_project(config)
            logging.info(CURRENT_PROJECT)
        else:
            raise ProjectNameNotSpecified('Project name not specified')
    except Exception as e:
        # logger.error(str(e))
        logger.exception(e)

def run_project(args):
    global CONFIG_FILE
    CONFIG_FILE = args.config
    
    RunIt.DOCKER = args.docker
    RunIt.KUBERNETES = args.kubernetes
    
    if not CONFIG_FILE and not args.file:
        raise FileNotFoundError
    else:
        if not RunIt.has_config_file() and not args.file:
            raise FileNotFoundError
        elif args.file:
            filename = args.file
            runtime = EXT_TO_RUNTIME[os.path.splitext(filename)[1]]
            LanguageParser.run_file(filename, runtime)
        else:
            project = RunIt(**RunIt.load_config())

            if args.shell:
                print(project.serve(args.function, args.arguments))
            elif args.expose:
                try:
                    asyncio.run(start_websocket(project))
                except KeyboardInterrupt:
                    sys.exit(1)
                except Exception:
                    sys.exit(1)
            else:
                start_webserver(project, args.host, args.port)

def clone(args):
    CURDIR = os.path.realpath(os.curdir)
    Account.isauthenticated({})
    user = Account.user()
    
    project_path = os.path.join(CURDIR, args.project_name)
    if not os.path.exists(project_path):
        os.mkdir(project_path)

    print(f'[+] Cloning project into {args.project_name}...')
    downloaded_file = Account.clone_project(args.project_name)

    filepath = os.path.join(project_path, f"{args.project_name}.zip")
    with open(filepath, 'wb') as zip_file:
        zip_file.write(downloaded_file)
    print('[!] Cloning complete')
    RunIt.extract_project(filepath)
    os.chdir(project_path)
    runit = RunIt(**RunIt.load_config())
    print(runit)
    Thread(target=runit.install_dependency_packages, args=()).start()
        
def publish(args):
    global CONFIG_FILE
    CONFIG_FILE = args.config

    global BASE_HEADERS
    # token = load_token()

    # headers = {}
    # headers['Authorization'] = f"Bearer {token}"

    Account.isauthenticated({})
    user = Account.user()

    os.chdir(CURRENT_PROJECT_DIR)

    config = RunIt.load_config()
    if not config:
        raise FileNotFoundError
    
    project = RunIt(**config)
    if user:
        project.author['name'] = user['name']       # type: ignore
        project.author['email'] = user['email']     # type: ignore

    project.update_config()
    print('[-] Preparing project for upload...')
    filename = project.compress()
    print('[#] Project files compressed')
    #print(project.config)

    print('[-] Uploading file....', end='\r')
    file = open(filename, 'rb')
    files = {'file': file}
    result = Account.publish_project(files, project.config)
    file.close()
    os.chdir(CURRENT_PROJECT_DIR)
    os.unlink(filename)

    if 'detail' in result.keys():
        print(result['detail'])
        exit(1)
    elif 'message' in result.keys():
        print(result['message'])
        exit(1)
    
    print('[#] Files Uploaded!!!')
    if 'project_id' in result.keys():
        project._id = result['project_id']
        project.homepage = result['homepage']
        project.update_config()
        print('[*] Project config updated')
        # if find_dotenv():
        #     set_key(find_dotenv(), 'RUNIT_PROJECT_ID', result['project_id'])

    print('[*] Project published successfully')
    print('[!] Access your functions with the urls below:')

    for func_url in result['functions']:
        print(f"[-] {func_url}")

def setup_runit(args):
    '''
    Setup Runit server side api settings
    
    @params args
    @return None
    '''
    try:
        if not find_dotenv(str(Path(RUNIT_HOMEDIR, '.env'))):
            env_path = Path(RUNIT_HOMEDIR, '.env')
            env_path.touch()
            set_key(find_dotenv(), 'RUNIT_API_ENDPOINT', '')
            # set_key(find_dotenv(), 'RUNIT_PROJECT_ID', '')
            
        settings = dotenv_values(find_dotenv())
        
        if args.api:
            settings['RUNIT_API_ENDPOINT'] = args.api
        else:
            for key, value in settings.items():
                new_value = input(f'{key} [{value}]: ').strip()
                if new_value:
                    settings[key] = new_value 
                else:
                    logger.debug(f'{key} cannot be empty')
                    logger.info(f'Setting {key} to default [{value}]')
        
        for key, value in settings.items():
            set_key(find_dotenv(), key, str(value))
    except Exception as e:
        logger.error(str(e))

def load_token(access_token = None):
    with shelve.open('account') as account:
        if access_token is None and 'access_token' in account.keys():
            return account['access_token']
        if access_token:
            account['access_token'] = access_token
        else:
            account['access_token'] = ''
        return None

def is_file(string):
    if (os.path.isfile(os.path.join(os.curdir, string))):
        return open(string, 'rt')
    return False

def get_functions(args):
    config = RunIt.load_config()
    if not config:
        raise FileNotFoundError
    
    project = RunIt(**config)
    print(project.get_functions())

def print_help():
    global parser
    parser.print_help()

def get_arguments():
    global parser
    global VERSION
    
    subparsers = parser.add_subparsers()
    new_parser = subparsers.add_parser('new', help='Create new project or function')
    new_parser.add_argument("name", type=str, nargs="?", help="Name of the new project")          
    new_parser.add_argument('-l', '--language', type=str, choices=['multi', 'python', 'php', 'javascript'],
                        help="Language of the new project", default="multi")
    new_parser.add_argument('-r','--runtime', type=str,
                        help="Runtime of the project language. E.g: python3.11, node, php8")
    new_parser.add_argument('--private', action='store_true', 
                        help="Make project publicly accessible or not. Default is public.")
    new_parser.set_defaults(func=create_new_project)
    
    # run_parser = subparsers.add_parser('run', help='Run current|specified project|function')
    # run_parser.add_argument('function', default='index', type=str, nargs='?', help='Name of function to run')
    # run_parser.add_argument('--file', type=str, nargs='?', help='Name of file to run')
    # run_parser.add_argument('--shell', action='store_true', help='Run function only in shell')
    # run_parser.add_argument('-x', '--arguments', action='append', default=[], help='Comma separated function arguments')
    # run_parser.set_defaults(func=run_project)

    login_parser = subparsers.add_parser('login', help="User account login")
    login_parser.add_argument('--email', type=str, help="Account email address")
    login_parser.add_argument('--password', type=str, help="Account password")
    login_parser.set_defaults(func=Account.login)

    register_parser = subparsers.add_parser('register', help="Register new account")
    register_parser.add_argument('--name', type=str, help="Account user's name")
    register_parser.add_argument('--email', type=str, help="Account email address")
    register_parser.add_argument('--password', type=str, help="Account password")
    register_parser.set_defaults(func=Account.register)

    account_parser = subparsers.add_parser('account', help='Get Current logged in user info')
    account_parser.add_argument('-i', '--info', action='store_true', help="Print out current account info")
    account_parser.set_defaults(func=Account.info)
    
    projects_parser = subparsers.add_parser('projects', help='Manage projects')
    projects_parser.add_argument('-l', '--list', action='store_true', help="List account projects")
    projects_parser.add_argument('--id', type=str, help="Project ID")
    projects_parser.set_defaults(func=Account.projects)

    projects_subparser = projects_parser.add_subparsers()

    new_project_parser = projects_subparser.add_parser('new', help="Create new Project")
    new_project_parser.add_argument('name', type=str, help="Name of project")
    new_project_parser.set_defaults(func=create_new_project)

    update_project_parser = projects_subparser.add_parser('update', help="Update Project by Id")
    update_project_parser.add_argument('--id', required=True, help="Id of the project to be updated")
    update_project_parser.add_argument('-d', '--data', required=True, type=str, action='append', help='A dictionary or string. E.g: name="new name" or {"name": "new name"}')
    update_project_parser.set_defaults(func=Account.update_project)

    delete_project_parser = projects_subparser.add_parser('rm', help="Delete Project")
    delete_project_parser.add_argument('--id', required=True, help="Id of the project to be deleted")
    delete_project_parser.set_defaults(func=Account.delete_project)

    functions_parser = subparsers.add_parser('functions', help='Manage functions')
    functions_parser.add_argument('-l', '--list', action='store_true', help="List project functions")
    functions_parser.add_argument('--id', type=str, help="Function ID")
    functions_parser.add_argument('-p', '--project', type=str, help="Project ID")
    functions_parser.set_defaults(func=get_functions)
    
    setup_parser = subparsers.add_parser('setup', help='Runit server-side configuration')
    setup_parser.add_argument('--api', type=str, help="Runit server-side api endpoint")
    setup_parser.set_defaults(func=setup_runit)

    publish_parser = subparsers.add_parser('publish', help='Publish current project')
    publish_parser.set_defaults(func=publish)
    
    clone_parser = subparsers.add_parser('clone', help='Publish project to current directory')
    clone_parser.add_argument('project_name', type=str, help='Name of project to clone')
    clone_parser.set_defaults(func=clone)
    
    parser.add_argument('--docker', action='store_true', help="Run program in docker container")
    parser.add_argument('--kubernetes', action='store_true', help="Run program using kubernetes")
    parser.add_argument('-f', '--function', default='index', type=str, nargs='?', help='Name of function to run')
    parser.add_argument('--file', type=str, nargs='?', help='Name of file to run')
    parser.add_argument('--shell', action='store_true', help='Run function only in shell')
    parser.add_argument('--expose', action='store_true', help='Expose local project on configured domain')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address to run project on')
    parser.add_argument('--port', type=int, default=5000, help='Host port to run project on')
    parser.add_argument('-x', '--arguments', action='append', default=[], help='Comma separated function arguments')
    parser.add_argument('-c','--config', type=is_file, default='runit.json', 
                        help="Configuration File, defaults to 'runit.json'") 
    parser.add_argument('-v','--version', action='version', version=f'%(prog)s {VERSION}')
    parser.set_defaults(func=run_project)
    return parser.parse_args()

def main():
    global parser
    try:
        parser = argparse.ArgumentParser(description="A terminal client for runit")
        args = get_arguments()
        args.func(args)

    except FileNotFoundError:
        print('No runit project or file to run\n')
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
