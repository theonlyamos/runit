#! python

import os
import sys
import json
import logging
from pathlib import Path
from zipfile import ZipFile
from io import TextIOWrapper
from typing import Optional, Union, Callable
from threading import Thread

from dotenv import load_dotenv

from .languages import LanguageParser
from .constants import (
    TEMPLATES_FOLDER, STARTER_FILES, NOT_FOUND_FILE,
    CONFIG_FILE, STARTER_CONFIG_FILE, IS_RUNNING, PROJECTS_DIR,
    CURRENT_PROJECT_DIR, DOT_RUNIT_IGNORE, INSTALL_MODULE_LATER_MESSAGE
)
 
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger('runit.log')

load_dotenv()

class RunIt:
    DOCKER = False
    KUBERNETES = False
    RUNTIME_ENV = os.getenv('RUNIT_RUNTIME', 'client')
    PYTHON_PATHS = {
        'win32': os.path.join(os.curdir, 'venv', 'Scripts', 'python.exe'),
        'linux': os.path.join(os.curdir, 'venv', 'bin', 'python')
    }

    def __init__(self, name, _id="", version="0.0.1", description="", homepage="",
    language="", runtime="", start_file="", private=False, author=None, is_file: bool = False):
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
            packages_install_thread = Thread(target=self.install_dependency_packages, args=())
            packages_install_thread.start()
        
        self.PYTHON_PATHS = {
            'win32': os.path.join(os.curdir, 'venv', 'Scripts', 'python.exe'),
            'linux': os.path.join(os.curdir, 'venv', 'bin', 'python')
        }
    
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
    def set_project_name(name: Optional[str] = None)-> str:
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
    
    @staticmethod
    def notfound(format='json'):
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE

        if format == 'json':
            return '404 - Not Found'

        with open(os.path.join(os.curdir, TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
    @staticmethod
    def extract_project(filepath):
        directory = os.path.split(filepath)[0]
    
        with ZipFile(filepath, 'r') as file:
            file.extractall(directory)
        os.unlink(filepath)
    
    def get_functions(self)->list:
        if 'python' in self.runtime:
            self.runtime = os.path.realpath(self.PYTHON_PATHS[sys.platform])
        
        lang_parser = LanguageParser.detect_language(
            filename=self.start_file, 
            runtime=self.runtime, 
            is_docker=RunIt.DOCKER, 
            project_id=self._id
        )
        return lang_parser.list_functions()
    
    @staticmethod
    def dockerize(project_path: str):
        '''
        Create docker image for project

        @params project_path
        @return None
        '''
        try:
            import docker

            client = docker.from_env()

            project_id = os.path.split(project_path)[-1]
            logger.info(f"[-] Building image for {project_id}")

            image = client.images.build(
                path=project_path,
                tag=project_id,
            )
            logger.info(image)

        except ImportError:
            logger.warning('[!] Docker package not installed.')
            logger.debug('[-] Use `pip install docker` to install the package.')
            sys.exit(1)
        except Exception as e:
            logger.exception(str(e))
            sys.exit(1)
    
    @staticmethod
    def run_background_task(target: Callable, *args: list):
        '''
        Runction for running threads

        @param target Function to run
        @param args Arguments for the function
        @return None
        '''
        bg_thread = Thread(target=target, args=(args))
        bg_thread.start()
        bg_thread.join()

    @classmethod
    def is_private(cls, project_id: str, projects_folder: str = PROJECTS_DIR)-> bool:
        global NOT_FOUND_FILE

        os.chdir(projects_folder)
        
        if not RunIt.has_config_file():
            return False
        
        project = cls(**RunIt.load_config())
        return project.private

    @classmethod
    def start(cls, project_id: str, func='index', projects_folder: str = PROJECTS_DIR, args: Optional[Union[dict,list]]=None):
        global NOT_FOUND_FILE

        os.chdir(projects_folder)
        
        if not RunIt.has_config_file():
            return RunIt.notfound()
        
        project = cls(**RunIt.load_config())
        
        
        if 'python' in project.runtime:
            project.runtime = cls.PYTHON_PATHS[sys.platform]

        if type(args) is dict:
            args = list(args.values())

        args_list = args if type(args) is list  else []
        
        start_file = project.start_file

        lang_parser = LanguageParser.detect_language(
            filename=start_file, 
            runtime=os.getenv('RUNTIME_'+project.language.upper(), project.runtime), 
            is_docker=RunIt.DOCKER, 
            project_id=project_id
        )
        lang_parser.current_func = func
        try:
            return getattr(lang_parser, func)(*args_list)
        except AttributeError as e:
            return RunIt.notfound()
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
    
    def serve(self, func: str = 'index', args: Optional[Union[dict,list]]=None):
        global NOT_FOUND_FILE
        
        if 'python' in self.runtime:
            self.runtime = self.PYTHON_PATHS[sys.platform]
        
        lang_parser = LanguageParser.detect_language(self.start_file, self.runtime)
        setattr(lang_parser, 'current_func', func)

        if type(args) is dict:
            args = list(args.values())

        args_list = args if type(args) is list  else []
        
        try:
            return getattr(lang_parser, func)(*args_list)
        except AttributeError as e:
            return RunIt.notfound()
        except TypeError as e:
            try:
                return getattr(lang_parser, func)()
            except TypeError as e:
                return str(e)
        except Exception as e:
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
    
    def get_exclude_list(self):
        exclude_list = [self.name + '.zip', 'account.db', '.git', '.venv', 'venv', 'Dockerfile']
        
        if os.path.exists(DOT_RUNIT_IGNORE):
            with open(DOT_RUNIT_IGNORE, 'rt') as file:
                exclude_list.extend(os.path.normpath(line.strip()) for line in file if line.strip())
        
        exclude_list = [item for item in exclude_list if item != '.']
        return exclude_list
    
    def compress(self):
        zipname = f'{self.name}.zip'
        exclude_list = self.get_exclude_list()

        with ZipFile(zipname, 'w') as zipobj:
            logger.info('[!] Compressing Project Files...')
            for folder_name, subfolders, filenames in os.walk(os.curdir):
                if any(os.path.normpath(os.path.dirname(folder_name)).split(os.path.sep)[0] not in exclude_list for filename in filenames):
                    for filename in filenames:
                        filepath = os.path.join(folder_name, filename)
                        if os.path.basename(filepath) not in exclude_list and '__pycache__' not in folder_name:
                            zipobj.write(filepath, filepath)
                            logger.info(f'[{filepath}] Compressed!')
            logger.info(f'[!] Filename: {zipname}')
            
        return zipname

    def create_config(self):
        self.config['_id'] = self._id
        self.config['name'] = self.name
        self.config['version'] = self.version
        self.config['description'] = self.description
        self.config['homepage'] = 'http://example.com/project_id/'
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
            if os.path.isfile(os.path.join(self.LANGUAGE_TEMPLATE_FOLDER,template_file)):
                with open(os.path.join(self.LANGUAGE_TEMPLATE_FOLDER,
                    template_file),'rt') as file:
                    with open(os.path.join(os.curdir, 
                                           self.name, 
                                           template_file), 'wt') as starter:
                        starter.write(file.read())
            
        with open(os.path.join(TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            with open(os.path.join(os.curdir, self.name, NOT_FOUND_FILE), 'wt') as error_404:
                error_404.write(file.read())
        
        with open(os.path.join(TEMPLATES_FOLDER, DOT_RUNIT_IGNORE),'rt') as file:
            with open(os.path.join(os.curdir, self.name, DOT_RUNIT_IGNORE), 'wt') as dotrunitignore:
                dotrunitignore.write(file.read())
    
    def install_dependency_packages(self):
        global PROJECTS_DIR

        project_path = os.path.realpath(os.path.join(os.curdir, self.name))
        if RunIt.RUNTIME_ENV == 'server':
            project_path = os.path.realpath(os.path.join(PROJECTS_DIR, self._id))
        
        if project_path != os.path.realpath(os.curdir):
            os.chdir(project_path)
        
        packaging_functions = {}
        packaging_functions['javascript'] = self.update_and_install_package_json
        packaging_functions['php'] = self.update_and_install_composer_json
        packaging_functions['python'] = self.install_python_packages
        packaging_functions['multi'] = self.install_all_language_packages
        packaging_functions[self.language]()
    
    def install_all_language_packages(self):
        try:
            logger.info("[+] Installing all packages...")
            self.update_and_install_package_json()
            self.update_and_install_composer_json()
            self.install_python_packages()
        except Exception:
            logger.warning("[!] Couldn't install packages")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
    
    def update_and_install_package_json(self):
        logger.info("[-] Creating and updating package.json")
        package_file = open('package.json', 'rt')
        package_details = json.load(package_file)
        package_file.close()
        
        package_details['name'] = self.name
        package_details['author'] = self.author
        
        package_file = open('package.json', 'wt')
        json.dump(package_details, package_file, indent=4)
        package_file.close()
        try:
            logger.info('[-] Installing node modules...')
            if RunIt.RUNTIME_ENV == 'client':
                os.system('npm install')
            else:
                os.system('bun install')
        except Exception as e:
            logger.exception(str(e))
            logger.error("[!] Couldn't install modules")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
        

    def update_and_install_composer_json(self):
        logger.info("[-] Creating and updating composer.json")
        package_file = open('composer.json', 'rt')
        package_details = json.load(package_file)
        package_file.close()
        
        package_details['name'] = f"runit/{self.name.replace('-', '_')}"
        package_details['author'] = self.author
        
        with open('composer.json', 'wt') as package_file:
            json.dump(package_details, package_file, indent=4)

        try:
            logger.info('[-] Installing php packages...')
            os.system('composer install')
        except Exception as e:
            logger.exception(str(e))
            logger.error("[!] Couldn't install packages")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
    
    def install_python_packages(self):
        venv_path = os.path.join(os.curdir, 'venv')
        
        if os.path.exists(venv_path):
            logger.info(msg="[-] Deleting old virtual environment...")
            rm_command = "rm -rf" if sys.platform != 'win32' else 'rm -r'
            os.system(f"{rm_command} {os.path.realpath(venv_path)}")
        
        logger.info(msg="[!] Creating virtual environment...")
        os.system("python -m venv venv")
        logger.info("[+] Created virtual environment")
        
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
        logger.info(f"--{os.path.realpath(pip_path)}")
        if sys.platform != 'win32':
            pip_path = f"{os.path.realpath(os.path.join(venv_path, 'bin', 'pip'))}"
        try:
            logger.info("[!] Installing python packages...")
            activate_install_instructions = f"""
            {pip_path} install -r requirements.txt
            """.strip()
            os.system(activate_install_instructions)
            logger.info("[+] Installed python packages")
        except Exception as e:
            logger.exception(str(e))
            logger.error("[!] Couldn't install packages")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
    

