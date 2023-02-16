#! python

import os
import sys
import json
from zipfile import ZipFile
from io import TextIOWrapper
from typing import Optional, Union

from flask import request
from dotenv import load_dotenv

from .languages import LanguageParser
from .constants import TEMPLATES_FOLDER, STARTER_FILES, NOT_FOUND_FILE, \
        CONFIG_FILE, STARTER_CONFIG_FILE, IS_RUNNING, PROJECTS_DIR, \
        CURRENT_PROJECT_DIR, DOT_RUNIT_IGNORE

load_dotenv()
class RunIt:
    def __init__(self, name, _id="", version="0.0.1", description="", homepage="",
    language="", runtime="", start_file="", private=False, author={}, is_file: bool = False):
        global STARTER_FILES

        self._id = _id
        self.name = name
        self.version = version
        self.description = description
        self.homepage = homepage
        self.language = language
        self.runtime = runtime
        self.private = private
        self.author = author
        self.config = {}
        self.start_file = start_file if start_file else STARTER_FILES[self.language]
        self.create_config()
        
        if not RunIt.has_config_file() and not is_file:
            self.create_folder()
            self.dump_config()
            self.create_starter_files()
            self.language_depending_packaging()
    
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
                
            while not name:
                name = str(input('Enter RunIt Name: '))
            return name
        except KeyboardInterrupt:
            sys.exit(1)


    @classmethod
    def start(cls, project_id: str, func='index', projects_folder: str = PROJECTS_DIR):
        global NOT_FOUND_FILE

        os.chdir(projects_folder)
        
        if not RunIt.has_config_file():
            return RunIt.notfound()
        
        project = cls(**RunIt.load_config())

        args = request.args
        
        args_list = []
        for key, value in args.items():
            args_list.append(value)
        
        start_file = project.start_file

        lang_parser = LanguageParser.detect_language(start_file, os.getenv('RUNTIME_'+project.language.upper(), project.runtime))
        lang_parser.current_func = func
        try:
            return getattr(lang_parser, func)(*args_list)
        except AttributeError as e:
            # return f"Function with name '{func}' not defined!"
            return RunIt.notfound()
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
    
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
        lang_parser = LanguageParser.detect_language(self.start_file, self.runtime)
        return lang_parser.list_functions()
    
    def serve(self, func: str = 'index', args: Optional[Union[dict,list]]=None, filename: str = ''):
        global NOT_FOUND_FILE
        global request

        lang_parser = LanguageParser.detect_language(self.start_file, self.runtime)
        lang_parser.current_func = func
        
        if not args and request:
            args = dict(request.args)

        args_list = args if type(args) == list else []
        
        if type(args) == dict:
            for key, value in args.items():
                args_list.append(value)

        try:
            return getattr(lang_parser, func)(*args_list)
        except AttributeError as e:
            return RunIt.notfound()
            # return f"Function with name '{func}' not defined!"
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
    
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
        self.config['runtime'] = self.runtime
        self.config['private'] = self.private
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
        json.dump(self.config, config_file, indent=4)
        config_file.close()
    
    def compress(self):
        os.chdir(CURRENT_PROJECT_DIR)

        zipname = f'{self.name}.zip'
        ignore_files = os.listdir(os.path.join(TEMPLATES_FOLDER, DOT_RUNIT_IGNORE))
        exclude_list = [zipname, 'account.db', *ignore_files]
        
        with ZipFile(zipname, 'w') as zipobj:
            print('[!] Compressing Project Files...')
            for folderName, subfolders, filenames in os.walk(os.curdir):
                for filename in filenames:
                    filepath = os.path.join(folderName,  filename)
                    
                    if not os.path.basename(filepath) in exclude_list and not '__pycache__' in folderName:
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
        self.config['runtime'] = self.runtime
        self.config['private'] = self.private
        self.config['start_file'] = self.start_file
        self.config['author'] = self.author
    
    def create_starter_files(self):
        global DOT_RUNIT_IGNORE
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE
        
        self.LANGUAGE_TEMPLATE_FOLDER = os.path.realpath(os.path.join(TEMPLATES_FOLDER, self.language))
        self.LANGUAGE_TEMPLATE_FILES = os.listdir(self.LANGUAGE_TEMPLATE_FOLDER)
        
        for template_file in self.LANGUAGE_TEMPLATE_FILES:
            with open(os.path.join(self.LANGUAGE_TEMPLATE_FOLDER,
                template_file),'rt') as file:
                with open(os.path.join(os.curdir, self.name, template_file), 'wt') as starter:
                    starter.write(file.read())
            
        with open(os.path.join(TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            with open(os.path.join(os.curdir, self.name, NOT_FOUND_FILE), 'wt') as error:
                error.write(file.read())
        
        with open(os.path.join(TEMPLATES_FOLDER, DOT_RUNIT_IGNORE),'rt') as file:
            with open(os.path.join(os.curdir, self.name, DOT_RUNIT_IGNORE), 'wt') as dotrunitignore:
                dotrunitignore.write(file.read())
    
    def language_depending_packaging(self):
        os.chdir(os.path.join(os.curdir, self.name))
        packaging_functions = {}
        packaging_functions['javascript'] = self.update_and_install_package_json
        packaging_functions['php'] = self.update_and_install_composer_json
        packaging_functions['python'] = self.install_python_packages
        
        packaging_functions[self.language]()
    
    def update_and_install_package_json(self):
        print("[-] Creating and updating package.json")
        package_file = open('package.json', 'rt')
        package_details = json.load(package_file)
        package_file.close()
        
        package_details['name'] = self.name
        package_details['author'] = self.author
        
        package_file = open('package.json', 'wt')
        json.dump(package_details, package_file, indent=4)
        package_file.close()
        # try:
        #     print('[-] Installing node modules...')
        #     os.system('npm install')
        # except Exception as e:
        #     print(str(e))
        #     print("[!] Couldn't install modules")
        #     print("[~] Try again manually later.")
        

    def update_and_install_composer_json(self):
        print("[-] Creating and updating composer.json")
        package_file = open('composer.json', 'rt')
        package_details = json.load(package_file)
        package_file.close()
        
        package_details['name'] = f"runit/{self.name.replace('-', '_')}"
        package_details['author'] = self.author
        
        package_file = open('composer.json', 'wt')
        json.dump(package_details, package_file, indent=4)
        package_file.close()
        # try:
        #     print('[-] Installing php packages...')
        #     os.system('composer install')
        # except Exception as e:
        #     print(str(e))
        #     print("[!] Couldn't install packages")
        #     print("[~] Try again manually later.")
    
    def install_python_packages(self):
        print("[-] Creating virtual environment")
        os.system(f"{self.runtime} -m venv venv")
        # try:
        #     print("[-] Installing python packages")
        #     activate_install_instructions = f"""
        #     {os.curdir}\\venv\\Scripts\\pip.exe install -r requirements.txt
        #     """.strip()
        #     os.system(activate_install_instructions)
        # except Exception as e:
        #     print(str(e))
        #     print("[!] Couldn't install packages")
        #     print("[~] Try again manually later.")