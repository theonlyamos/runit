#!python3
import inspect
from io import TextIOWrapper
import os
import sys
import json
import shelve
import getpass
import argparse
from zipfile import ZipFile

from flask import Flask, request
from subprocess import check_output

import requests

from modules.account import Account
from languages import LanguageParser

VERSION = "0.0.1"
CURRENT_PROJECT = ""
TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
STARTER_FILES = {'python3': 'application.py', 'php': 'index.php','nodejs': 'index.js'}
EXTENSIONS = {'python3': '.py',  'php': '.php', 'nodejs': '.js'}
NOT_FOUND_FILE = '404.html'
CONFIG_FILE = 'runit.json'
STARTER_CONFIG_FILE = 'runit.json'
IS_RUNNING = False
PROJECTS_DIR = os.path.join(os.getenv('RUNIT_HOMEDIR'), 'projects')
PROJECTS_API = 'http://'+os.getenv('RUNIT_SERVERNAME')+'/api/projects/'
BASE_HEADERS = {
    'Content-Type': 'application/json'
}

app = Flask(__name__)
app.secret = "dasf34sfkjfldskfa9usafkj0898fsdafdsaf"

def StartWebserver(project):
    global app
    try:
        app.add_url_rule('/', view_func=project.serve)
        app.add_url_rule('/<func>', view_func=project.serve)
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(e)

class RunIt:
    def __init__(self, name, _id="", version="0.0.0", description="", homepage="",
    lang="", framework="", runtime="", start_file="", author={}):
        global STARTER_FILES

        self._id = _id
        self.name = name
        self.version = version
        self.description = description
        self.homepage = homepage
        self.lang = lang if not lang.startswith('python') else 'python3'
        self.framework = framework
        self.runtime = runtime
        self.author = author
        self.config = {}
        self.start_file = start_file if start_file else STARTER_FILES[self.lang]
        self.create_config()
        
        if not RunIt.has_config_file():
            self.create_folder()
            self.dump_config()
            self.create_starter_files()
    
    def __repr__(self):
        return json.dumps(self.config, indent=4)

    @staticmethod
    def exists(name):
        return os.path.exists(os.path.join(os.curdir, name))

    @staticmethod
    def has_config_file():
        global CONFIG_FILE

        if isinstance(CONFIG_FILE, str):
            return os.path.exists(os.path.join(os.curdir, CONFIG_FILE))
        elif isinstance(CONFIG_FILE, bool):
            return False
        return True

    @staticmethod
    def load_config()-> dict:
        '''
        Load Configuration file from
        current directory: runit.json
        
        @params None
        @return Dictionary
        '''
        global CONFIG_FILE
        
        if isinstance(CONFIG_FILE, str):
            if os.path.exists(os.path.join(os.curdir, CONFIG_FILE)):
                with open(CONFIG_FILE, 'rt') as file:
                    return json.load(file)
        elif isinstance(CONFIG_FILE, TextIOWrapper):
            return json.load(CONFIG_FILE)
        return {}

    @staticmethod
    def set_project_name(name: str =None)-> str:
        '''
        Set Project name from argument
        or terminal input
        
        @param  name
        @return name
        '''
        global IS_RUNNING
        try:
            if not IS_RUNNING:
                IS_RUNNING = True
            else:
                name = str(input('Enter RunIt Name: '))
            while not name:
                name = str(input('Enter RunIt Name: '))
            return name
        except KeyboardInterrupt:
            sys.exit(1)

    @classmethod
    def run(cls, args):
        if not RunIt.has_config_file():
            print('No runit project to run')
            sys.exit(1)
        project = cls(**RunIt.load_config())

        if args.shell:
            project.serve(args.function, args.arguments)
        else:
            StartWebserver(project)
    
    @classmethod
    def start(cls, project_id: str, func='index'):
        global NOT_FOUND_FILE
        global PROJECTS_DIR

        os.chdir(os.path.join(PROJECTS_DIR, project_id))
        
        if not RunIt.has_config_file():
            return RunIt.notfound()
        
        project = cls(**RunIt.load_config())

        args = request.args
        print(args)
        start_file = project.start_file

        lang_parser = LanguageParser.detect_language(start_file)
        lang_parser.current_func = func
        try:
            return getattr(lang_parser, func)(**args)
        except AttributeError as e:
            return f"Function with name '{func}' not defined!"
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
        '''
        project = cls(**RunIt.load_config())

        if func == "index":
            start_file = project.start_file
        else:
            global EXTENSIONS
            extension = EXTENSIONS[project.lang]
            start_file = f'{func}{extension}'
        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{project.lang} {start_file}", shell=True)
            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'")
        
        with open(os.path.join(os.curdir, NOT_FOUND_FILE),'rt') as file:
            return file.read()
        '''
    
    @staticmethod
    def notfound():
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE

        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
    @staticmethod
    def extract_project(filepath):
        directory, filename = os.path.split(filepath)
        with ZipFile(filepath, 'r') as file:
            file.extractall(directory)
        os.unlink(filepath)
    
    def get_functions(self)->list:
        lang_parser = LanguageParser.detect_language(self.start_file)
        return [f[0] for f in inspect.getmembers(lang_parser, inspect.isfunction)]
    
    def serve(self, func='index', args=None):
        global NOT_FOUND_FILE

        start_file = self.start_file

        lang_parser = LanguageParser.detect_language(start_file)
        lang_parser.current_func = func
        try:
            return getattr(lang_parser, func)(*args)
        except AttributeError as e:
            return f"Function with name '{func}' not defined!"
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
        '''
        if func == "index":
            start_file = self.start_file
        else:
            global EXTENSIONS
            extension = EXTENSIONS[self.lang]
            start_file = f'{func}{extension}'
        

        import inspect
        sys.path.append(os.path.abspath(os.curdir))
        module = __import__(inspect.getmodulename(start_file))
        function = [f[1] for f in inspect.getmembers(module, inspect.isfunction) if f[0] == func]
        if function:
            function[0]()

        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{self.lang} {start_file}", shell=True)
            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'")
        
        with open(os.path.join(os.curdir, NOT_FOUND_FILE),'rt') as file:
            return file.read()
        '''
    
    def create_folder(self):
        os.mkdir(os.path.join(os.curdir, self.name))

    def dump_config(self):
        global CONFIG_FILE

        if isinstance(CONFIG_FILE, str):
            config_file = open(os.path.join(os.curdir, self.name,
            CONFIG_FILE),'wt')
        else:
            config_file = CONFIG_FILE

        json.dump(self.config, config_file, indent=4)
        config_file.close()

    def update_config(self):
        global CONFIG_FILE
        global STARTER_CONFIG_FILE

        if isinstance(CONFIG_FILE, TextIOWrapper):
            CONFIG_FILE.close()
            CONFIG_FILE = STARTER_CONFIG_FILE
        
        config_file = open(CONFIG_FILE,'wt')
        self.config['_id'] = self._id
        json.dump(self.config, config_file, indent=4)
        config_file.close()
    
    def compress(self):
        import os
        from zipfile import ZipFile

        zipname = f'{self.name}.zip'
        with ZipFile(zipname, 'w') as zipobj:
            print('[!] Compressing Project Files...')
            for folderName, subfolders, filenames in os.walk(os.curdir):
                for filename in filenames:
                    filepath = os.path.join(folderName,  filename)
                    #print(filepath)
                    if os.path.basename(filepath) != zipname:
                        print(f'[{filepath}] Compressing', end='\r')
                        zipobj.write(filepath, filepath)
                        print(f'[{filepath}] Compressed!')
            print(f'[!] Filename: {zipname}')
        return zipname

    def create_config(self):
        self.config['_id'] = self._id
        self.config['name'] = self.name
        self.config['version'] = self.version
        self.config['description'] = self.description
        self.config['homepage'] = self.homepage
        self.config['lang'] = self.lang
        self.config['framework'] = self.framework
        self.config['runtime'] = self.runtime
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
        self.config['author']['name'] = getpass.getuser()
        self.config['author']['website'] = ""
    
    def create_starter_files(self):
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE
        
        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, self.lang,
            self.start_file),'rt') as file:
            with open(os.path.join(os.curdir, self.name, self.start_file), 'wt') as starter:
                starter.write(file.read())
        
        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            with open(os.path.join(os.curdir, self.name, NOT_FOUND_FILE), 'wt') as error:
                error.write(file.read())
        
        '''
        with open(os.path.join(os.curdir, 'runit-cli.py'),'rt') as file:
            with open(os.path.join(os.curdir, self.name, 'runit-cli.py'), 'wt') as client:
                client.write(file.read())
        '''

        if self.lang.startswith('python'):
            PACKAGES_FOLDER = 'packages'
            os.mkdir(os.path.join(os.curdir, self.name, PACKAGES_FOLDER))
            for filename in os.listdir(os.path.abspath(os.path.join(os.curdir, TEMPLATES_FOLDER, self.lang, PACKAGES_FOLDER))):
                if os.path.isfile(os.path.join(os.curdir, TEMPLATES_FOLDER, self.lang,
                    PACKAGES_FOLDER, filename)):
                    with open(os.path.join(os.curdir, TEMPLATES_FOLDER, self.lang,
                        PACKAGES_FOLDER, filename),'rt') as file:
                        with open(os.path.join(os.curdir, self.name, PACKAGES_FOLDER, filename), 'wt') as package:
                            package.write(file.read())

def load_token(access_token: str|None = None):
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
        CURRENT_PROJECT = RunIt(name=args.name, lang=args.lang, 
                                runtime=args.runtime)
        print(CURRENT_PROJECT)
    else:
        print('Project name not specified')

def run_project(args):
    global CONFIG_FILE
    CONFIG_FILE = args.config

    if CONFIG_FILE:
        RunIt.run(args)
    else:
        raise FileNotFoundError

def publish(args):
    global CONFIG_FILE
    CONFIG_FILE = args.config

    global BASE_HEADERS
    token = load_token()

    headers = {}
    headers['Authorization'] = f"Bearer {token}"

    config = RunIt.load_config()
    #config.update({})
    if not config:
        raise FileNotFoundError
    
    project = RunIt(**config)
    #project.update_config()
    print('[-] Preparing project for upload...')
    filename = project.compress()
    print('[#] Project files compressed')
    #print(project.config)

    print('[-] Uploading file....', end='\r')
    with open(filename, 'rb') as file:
        files = {'file': file}
        req = requests.post(PROJECTS_API, data=project.config, 
                            files=files, headers=headers)
        print('[#] File Uploaded!!!')
    os.unlink(filename)
    result = req.json()

    if 'msg' in result.keys():
        print(result['msg'])
        exit(1)
    elif 'message' in result.keys():
        print(result['message'])

    if 'project_id' in result.keys():
        project._id = result['project_id']
        print(project._id)
        project.update_config()
        print('[*] Project config updated')

    print('[*] Project published successfully')
    print('[!] Access your functions with the urls below:')

    for func_url in result['functions']:
        print(f"[-] {func_url}")



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
    new_parser.add_argument('-L', '--lang', type=str, choices=['python3', 'python', 'php', 'nodejs'], default='python', 
                        help="Language of the new project")
    new_parser.add_argument('-R','--runtime', type=str,
                        help="Runtime of the project language. E.g: python3, node")
    new_parser.set_defaults(func=create_new_project)
    
    run_parser = subparsers.add_parser('run', help='Run current|specified project|function')
    run_parser.add_argument('--shell', action='store_true', help='Run function only in shell')
    run_parser.add_argument('-f', '--function', default='index', type=str, help='Function to run')
    run_parser.add_argument('-x', '--arguments', action='append', default=[], help='Comma separated function arguments')
    run_parser.set_defaults(func=run_project)

    login_parser = subparsers.add_parser('login', help="User account login")
    login_parser.add_argument('--email', type=str, help="Account email address")
    login_parser.add_argument('--password', type=str, help="Account password")
    login_parser.set_defaults(func=Account.login)

    register_parser = subparsers.add_parser('register', help="Register new account")
    register_parser.add_argument('--name', type=str, help="Account user's name")
    register_parser.add_argument('--email', type=str, help="Account email address")
    register_parser.add_argument('--password', type=str, help="Account password")
    register_parser.set_defaults(func=Account.register)

    account_parser = subparsers.add_parser('account', help='Run command on user account')
    #user_subparser = account_parser.add_subparsers()

    account_parser.add_argument('-i', '--info', action='store_true', help="Print out current account info")
    account_parser.set_defaults(func=Account.info)
    
    projects_parser = subparsers.add_parser('projects', help='Manage projects')
    projects_parser.add_argument('-l', '--list', action='store_true', help="List account projects")
    projects_parser.add_argument('-i', '--id', type=str, help="Project ID")
    projects_parser.set_defaults(func=Account.projects)

    projects_subparser = projects_parser.add_subparsers()

    new_project_parser = projects_subparser.add_parser('new', help="Create new Project")
    new_project_parser.add_argument('name', type=str, help="Name of project")
    new_project_parser.set_defaults(func=create_new_project)

    update_project_parser = projects_subparser.add_parser('update', help="Update Project by Id")
    update_project_parser.add_argument('-i', '--id', required=True, help="Id of the project to be updated")
    update_project_parser.add_argument('-d', '--data', required=True, type=str, action='append', help='A dictionary or string. E.g: name="new name" or {"name": "new name"}')
    update_project_parser.set_defaults(func=Account.update_project)

    delete_project_parser = projects_subparser.add_parser('rm', help="Delete Project")
    delete_project_parser.add_argument('-i', '--id', required=True, help="Id of the project to be deleted")
    delete_project_parser.set_defaults(func=Account.delete_project)

    functions_parser = subparsers.add_parser('functions', help='Manage functions')
    functions_parser.add_argument('-l', '--list', action='store_true', help="List project functions")
    functions_parser.add_argument('-i', '--id', type=str, help="Function ID")
    functions_parser.add_argument('-p', '--project', type=str, help="Project ID")
    functions_parser.set_defaults(func=Account.functions)

    publish_parser = subparsers.add_parser('publish', help='Create new project or function')
    publish_parser.set_defaults(func=publish)
    parser.add_argument('-C','--config', type=is_file, default='runit.json', 
                        help="Configuration File, defaults to 'runit.json'") 
    parser.add_argument('-V','--version', action='version', version=f'%(prog)s {VERSION}')
    parser.set_defaults(func=print_help)
    return parser.parse_args()

    
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="A terminal client for runit")
        args = get_arguments()
        args.func(args)

    except FileNotFoundError:
        print("Config file not found")
        #parser.print_help()