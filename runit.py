#! /usr/bin/python3
import os
import sys
import json
import argparse
from subprocess import check_output
from flask import Flask
from Request import Request

VERSION = "0.0.1"
CURRENT_PROJECT = ""
TEMPLATES_FOLDER = os.path.join(os.curdir, 'templates')
STARTER_FILES = {'python': 'app.py', 'python3': 'app.py', 'php': 
                 'index.php','nodejs': 'index.js'}
EXTENSIONS = {'python': '.py', 'python3': '.py', 'php': '.php', 'nodejs': '.js'}
NOT_FOUND_FILE = '404.html'
CONFIG_FILE = 'runit.json'
is_running = False

app = Flask(__name__)
app.secret = "dasf34sfkjfldskfa9usafkj0898fsdafdsaf"


def StartWebserver(project):
    global app
    try:
        app.add_url_rule('/', view_func=project.serve)
        app.add_url_rule('/<page>', view_func=project.serve)
        app.run(debug=True, port=9000)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(e)

class RunIt:
    def __init__(self, name, version="0.0.0", description="", homepage="",
    lang="", framework="", runtime="", start_file="", author={}):
        global STARTER_FILES

        self.name = name
        self.version = version
        self.description = description
        self.homepage = homepage
        self.lang = lang
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
    def load_config():
        global CONFIG_FILE

        if isinstance(CONFIG_FILE, str):
            if os.path.exists(os.path.join(os.curdir, CONFIG_FILE)):
                with open(CONFIG_FILE, 'rt') as file:
                    return json.load(file)
        elif not isinstance(CONFIG_FILE, bool):
            return json.load(CONFIG_FILE)
        return {}

    @staticmethod
    def set_project_name(name=""):
        global is_running
        try:
            if not is_running:
                is_running = True
            else:
                name = str(input('Enter RunIt Name: '))
            while not name:
                name = str(input('Enter RunIt Name: '))
            return name
        except KeyboardInterrupt:
            sys.exit(1)

    @classmethod
    def run(cls):
        if not RunIt.has_config_file():
            print('No runit project to run')
            sys.exit(1)
        project = cls(**RunIt.load_config())

        StartWebserver(project)
    
    @classmethod
    def start(cls, account, page='index'):
        global NOT_FOUND_FILE

        os.chdir(os.path.join('accounts', account))
        
        if not RunIt.has_config_file():
            return '404 - No project to run'
        project = cls(**RunIt.load_config())

        if page == "index":
            start_file = project.start_file
        else:
            global EXTENSIONS
            extension = EXTENSIONS[project.lang]
            start_file = f'{page}{extension}'
        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{project.lang} {start_file}", shell=True)
            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'")
        
        with open(os.path.join(os.curdir, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
    @classmethod
    def notfound(cls):
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE

        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
    def serve(self, page='index'):
        global NOT_FOUND_FILE
        if page == "index":
            start_file = self.start_file
        else:
            global EXTENSIONS
            extension = EXTENSIONS[self.lang]
            start_file = f'{page}{extension}'
        
        if os.path.isfile(os.path.join(os.curdir, start_file)):
            command = check_output(f"{self.lang} {start_file}", shell=True)
            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'")
        
        with open(os.path.join(os.curdir, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
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

    def create_config(self):
        self.config['name'] = self.name
        self.config['version'] = self.version
        self.config['description'] = self.description
        self.config['homepage'] = self.homepage
        self.config['lang'] = self.lang
        self.config['framework'] = self.framework
        self.config['runtime'] = self.runtime
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
        self.config['author']['name'] = ""
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
        
        with open(os.path.join(os.curdir, 'runit-cli.py'),'rt') as file:
            with open(os.path.join(os.curdir, self.name, 'runit-cli.py'), 'wt') as client:
                client.write(file.read())

def is_file(string):
    if (os.path.isfile(os.path.join(os.curdir, string))):
        return open(string, 'r+')
    return False

def get_arguments():
    global parser
    global VERSION
    
    parser.add_argument("action", type=str, choices=['new','run'],
                        help="Action to perform")
    parser.add_argument("name", type=str, nargs="?", 
                        help="Name of the new project")
    parser.add_argument('-v','--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-c','--config', type=is_file, default='runit.json', 
                        help="Configuration File, defaults to 'runit.json'")
    parser.add_argument('-l', '--lang', type=str, choices=['python', 'python3', 'php', 'nodejs'], default='python', 
                        help="Language of the new project")
    parser.add_argument('-r','--runtime', type=str, default='python3', 
                        help="Runtime of the project language. E.g: python3, npm")
    return parser.parse_args()
    
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="A terminal client for runit")
        args = get_arguments()
        
        CONFIG_FILE = args.config
        if args.action == 'run':
            if CONFIG_FILE:
                RunIt.run()
            else:
                raise FileNotFoundError
        elif args.action == 'new' and args.name:
            name = RunIt.set_project_name(args.name)
            if RunIt.exists(name):
                print(f'{name} project already Exists')
                sys.exit(1)
            
            CONFIG_FILE = 'runit.json'
            CURRENT_PROJECT = RunIt(name=args.name, lang=args.lang, 
                                    runtime=args.runtime)
            print(CURRENT_PROJECT)

    except FileNotFoundError:
        print("Config file not found")
        #parser.print_help()
        
