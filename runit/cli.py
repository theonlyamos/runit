import os
import sys
import shelve
import getpass
import argparse
import asyncio
from typing import Type, Optional
from threading import Thread

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import json

from .languages import LanguageParser
from .modules import Account
from .runit import RunIt

from .constants import VERSION, CURRENT_PROJECT, CURRENT_PROJECT_DIR, EXT_TO_RUNTIME, \
                        LANGUAGE_TO_RUNTIME, RUNIT_HOMEDIR, SERVER_HOST, SERVER_PORT

load_dotenv()

def StartWebserver(project: RunIt, host: str = SERVER_HOST, port: int = SERVER_PORT):
    app = FastAPI()
    app.secret_key = "fdakfjlfdsaflfkjbasdoiefanckdareafasdfkowadbfakidfadfkj"
    
    @app.api_route('/', methods=["GET", "POST"])
    @app.api_route('/{func}', methods=["GET", "POST"])
    @app.api_route('/{func}/', methods=["GET", "POST"])
    @app.api_route('/{func}/{output_format}', methods=["GET", "POST"])
    @app.api_route('/{func}/{output_format}/', methods=["GET", "POST"])
    async def serve(func: str = 'index', output_format: str = 'json', request: Request = None):
        response = {'status': True, 'data': {}}
        result = ''
        try:
            parameters = request.query_params._dict
            if 'content-type' in request.headers.keys() and request.headers['content-type'] == "application/json":
                data = await request.json()
                parameters = {**parameters, **data}
            
            if 'output_format' in parameters.keys():
                del parameters['output_format']

            params = list(parameters.values()) if request else request
            result = project.serve(func, params) \
                if len(params) else project.serve(func)
            
            if result.startswith('404'):
                raise RuntimeError('Not Found')
            if output_format == 'html':
                return HTMLResponse(result)
            else:
                response['data'] = json.loads(result.replace("'", '"'))
                return response

        except json.decoder.JSONDecodeError:
            response['data'] = result
            return response
        except Exception:
            response['status'] = False
            response['message'] = RunIt.notfound(output_format)
            return HTMLResponse(RunIt.notfound(output_format)) if \
                output_format == 'html' else response
    
    try:
        import uvicorn
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        import sys
        sys.exit(1)
    except Exception as e:
        print(e)
        import sys
        sys.exit(1)

def create_new_project(args):
    global CONFIG_FILE
    global CURRENT_PROJECT
    '''
    Method for creating new project or
    function from command line arguments

    @param args Arguments from argparse
    @return None
    '''
    
    if args.name:
        name = RunIt.set_project_name(args.name)
        if RunIt.exists(name):
            print(f'{name} project already Exists')
            sys.exit(1)
        
        CONFIG_FILE = 'runit.json'
        config = {}
        config['name'] = args.name
        config['language'] = args.language
        config['runtime'] = args.runtime if args.runtime else LANGUAGE_TO_RUNTIME[args.language]
        config['private'] = args.private
        config['author'] = {}
        config['author']['name'] = getpass.getuser()
        config['author']['email'] = "name@example.com"
        
        user = Account.user()
        os.chdir(CURRENT_PROJECT_DIR)
        if user is not None:
            config['author']['name'] = user['name']
            config['author']['email'] = user['email']
        
        CURRENT_PROJECT = RunIt(**config)
        print(CURRENT_PROJECT)
    else:
        print('Project name not specified')

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
            else:
                StartWebserver(project, args.host, args.port)

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
        project.author['name'] = user['name']
        project.author['email'] = user['email']

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

    if 'msg' in result.keys():
        print(result['msg'])
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
    Setup Runit server side api
    
    @params args
    @return None
    '''
    if not find_dotenv():
        with open(os.path.join(RUNIT_HOMEDIR, '.env'), 'wt') as env_file:
            pass
        set_key(find_dotenv(), 'RUNIT_API_ENDPOINT', '')
        set_key(find_dotenv(), 'RUNIT_PROJECT_ID', '')
        
    settings = dotenv_values(find_dotenv())
    
    if args.api:
        settings['RUNIT_API_ENDPOINT'] = args.api
    else:
        for key, value in settings.items():
            new_value = input(f'{key} [{value}]: ').strip()
            if new_value:
                settings[key] = new_value 
            else:
                print(f'{key} cannot be empty')
                print(f'Setting {key} to default [{value}]')
    
    for key, value in settings.items():
        set_key(find_dotenv(), key, value)

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

def print_help(args):
    global parser
    parser.print_help()

def get_arguments():
    global parser
    global VERSION
    
    subparsers = parser.add_subparsers()
    new_parser = subparsers.add_parser('new', help='Create new project or function')
    new_parser.add_argument("name", type=str, nargs="?", 
                        help="Name of the new project")          
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
