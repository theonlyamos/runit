#!python3

import os
import sys
import json
import shelve
import inspect
import getpass
import argparse
from io import TextIOWrapper

from zipfile import ZipFile
from flask import Flask, request
from dotenv import load_dotenv


from .modules import Account
from .languages import LanguageParser

load_dotenv()

VERSION = "0.0.1"
CURRENT_PROJECT = ""
TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
STARTER_FILES = {'python': 'application.py', 'php': 'index.php','javascript': 'main.js'}
EXTENSIONS = {'python': '.py',  'php': '.php', 'javascript': '.js'}
NOT_FOUND_FILE = '404.html'
CONFIG_FILE = 'runit.json'
STARTER_CONFIG_FILE = 'runit.json'
IS_RUNNING = False
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'projects')
CURRENT_PROJECT_DIR = os.path.realpath(os.curdir)
BASE_HEADERS = {
    'Content-Type': 'application/json'
}

app = Flask(__name__)
app.secret = os.getenv('RUNIT_SECRET_KEY')

def StartWebserver(project):
    global app
    try:
        app.add_url_rule('/', view_func=project.serve)
        app.add_url_rule('/<func>', view_func=project.serve)
        app.add_url_rule('/<func>/', view_func=project.serve)
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(e)

class RunIt:
    def __init__(self, name, _id="", version="0.0.1", description="", homepage="",
    language="", framework="", runtime="", start_file="", author={}):
        global STARTER_FILES

        self._id = _id
        self.name = name
        self.version = version
        self.description = description
        self.homepage = homepage
        self.language = language
        self.framework = framework
        self.runtime = runtime
        self.author = author
        self.config = {}
        self.start_file = start_file if start_file else STARTER_FILES[self.language]
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
            print(project.serve(args.function, args.arguments))
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
        
        args_list = []
        for key, value in args.items():
            args_list.append(value)
        
        start_file = project.start_file

        lang_parser = LanguageParser.detect_language(start_file)
        lang_parser.current_func = func
        try:
            return getattr(lang_parser, func)(*args_list)
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
            extension = EXTENSIONS[project.language]
            start_file = f'{func}{extension}'
        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{project.language} {start_file}", shell=True)
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
        return lang_parser.list_functions()
    
    def serve(self, func='index', args=None):
        global NOT_FOUND_FILE

        lang_parser = LanguageParser.detect_language(self.start_file)
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
            extension = EXTENSIONS[self.language]
            start_file = f'{func}{extension}'
        

        import inspect
        sys.path.append(os.path.abspath(os.curdir))
        module = __import__(inspect.getmodulename(start_file))
        function = [f[1] for f in inspect.getmembers(module, inspect.isfunction) if f[0] == func]
        if function:
            function[0]()
        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{self.language} {start_file}", shell=True)
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
        self.config['name'] = self.name
        self.config['version'] = self.version
        self.config['description'] = self.description
        self.config['homepage'] = self.homepage
        self.config['language'] = self.language
        self.config['framework'] = self.framework
        self.config['runtime'] = self.runtime
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
        json.dump(self.config, config_file, indent=4)
        config_file.close()
    
    def compress(self):
        os.chdir(CURRENT_PROJECT_DIR)

        zipname = f'{self.name}.zip'
        exclude_list = [zipname, 'account.db']
        with ZipFile(zipname, 'w') as zipobj:
            print('[!] Compressing Project Files...')
            for folderName, subfolders, filenames in os.walk(os.curdir):
                for filename in filenames:
                    filepath = os.path.join(folderName,  filename)
                    #print(filepath)
                    print(os.path.basename(filepath), zipname, os.path.basename(filepath) != zipname)
                    if not os.path.basename(filepath) in exclude_list:
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
        self.config['homepage'] = 'https://example.com/project_id/'
        self.config['language'] = self.language
        self.config['framework'] = self.framework
        self.config['runtime'] = self.runtime
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
    
    def create_starter_files(self):
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE
        
        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, self.language,
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

        if self.language.startswith('python'):
            PACKAGES_FOLDER = 'packages'
            os.mkdir(os.path.join(os.curdir, self.name, PACKAGES_FOLDER))
            for filename in os.listdir(os.path.abspath(os.path.join(os.curdir, TEMPLATES_FOLDER, self.language, PACKAGES_FOLDER))):
                if os.path.isfile(os.path.join(os.curdir, TEMPLATES_FOLDER, self.language,
                    PACKAGES_FOLDER, filename)):
                    with open(os.path.join(os.curdir, TEMPLATES_FOLDER, self.language,
                        PACKAGES_FOLDER, filename),'rt') as file:
                        with open(os.path.join(os.curdir, self.name, PACKAGES_FOLDER, filename), 'wt') as package:
                            package.write(file.read())

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
        config['runtime'] = args.runtime
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

    print('[*] Project published successfully')
    print('[!] Access your functions with the urls below:')

    print(f"[-] {result['homepage']}")
    for func_url in result['functions']:
        print(f"[-] {func_url}")


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
    new_parser.add_argument('-L', '--language', type=str, choices=['python', 'php', 'javascript'],
                        help="Language of the new project")
    new_parser.add_argument('-R','--runtime', type=str,
                        help="Runtime of the project language. E.g: python3.10, node")
    new_parser.set_defaults(func=create_new_project)
    
    run_parser = subparsers.add_parser('run', help='Run current|specified project|function')
    run_parser.add_argument('function', default='index', type=str, nargs='?', help='Name of function to run')
    run_parser.add_argument('--shell', action='store_true', help='Run function only in shell')
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

    account_parser.add_argument('-I', '--info', action='store_true', help="Print out current account info")
    account_parser.set_defaults(func=Account.info)
    
    projects_parser = subparsers.add_parser('projects', help='Manage projects')
    projects_parser.add_argument('-L', '--list', action='store_true', help="List account projects")
    projects_parser.add_argument('--id', type=str, help="Project ID")
    projects_parser.set_defaults(func=Account.projects)

    projects_subparser = projects_parser.add_subparsers()

    new_project_parser = projects_subparser.add_parser('new', help="Create new Project")
    new_project_parser.add_argument('name', type=str, help="Name of project")
    new_project_parser.set_defaults(func=create_new_project)

    update_project_parser = projects_subparser.add_parser('update', help="Update Project by Id")
    update_project_parser.add_argument('--id', required=True, help="Id of the project to be updated")
    update_project_parser.add_argument('-D', '--data', required=True, type=str, action='append', help='A dictionary or string. E.g: name="new name" or {"name": "new name"}')
    update_project_parser.set_defaults(func=Account.update_project)

    delete_project_parser = projects_subparser.add_parser('rm', help="Delete Project")
    delete_project_parser.add_argument('--id', required=True, help="Id of the project to be deleted")
    delete_project_parser.set_defaults(func=Account.delete_project)

    functions_parser = subparsers.add_parser('functions', help='Manage functions')
    functions_parser.add_argument('-L', '--list', action='store_true', help="List project functions")
    functions_parser.add_argument('--id', type=str, help="Function ID")
    functions_parser.add_argument('-P', '--project', type=str, help="Project ID")
    functions_parser.set_defaults(func=get_functions)

    publish_parser = subparsers.add_parser('publish', help='Create new project or function')
    publish_parser.set_defaults(func=publish)
    parser.add_argument('-C','--config', type=is_file, default='runit.json', 
                        help="Configuration File, defaults to 'runit.json'") 
    parser.add_argument('-V','--version', action='version', version=f'%(prog)s {VERSION}')
    parser.set_defaults(func=print_help)
    return parser.parse_args()

def main():
    global parser
    try:
        parser = argparse.ArgumentParser(description="A terminal client for runit")
        args = get_arguments()
        args.func(args)

    except FileNotFoundError:
        print("Config file not found")
        #parser.print_help()
    
if __name__ == "__main__":
    main()
