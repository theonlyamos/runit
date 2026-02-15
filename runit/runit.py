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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    level=logging.INFO
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
        self._lang_parser = None
        self._lang_parser_mtime = None
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
    
    @property
    def lang_parser(self):
        """Lazy-loaded language parser with file change detection."""
        if self.start_file and os.path.exists(self.start_file):
            current_mtime = os.path.getmtime(self.start_file)
            if self._lang_parser is None or self._lang_parser_mtime != current_mtime:
                runtime = self.runtime
                if 'python' in runtime:
                    runtime = os.path.realpath(self.PYTHON_PATHS[sys.platform])
                self._lang_parser = LanguageParser.detect_language(
                    filename=self.start_file,
                    runtime=runtime,
                    is_docker=RunIt.DOCKER,
                    project_id=self._id
                )
                self._lang_parser_mtime = current_mtime
        return self._lang_parser

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
                name = str(input('Enter RunIt Project Name: '))
            return name
        except KeyboardInterrupt:
            sys.exit(1)
    
    @staticmethod
    def notfound(format='json'):
        global TEMPLATES_FOLDER
        global NOT_FOUND_FILE

        if format == 'json':
            return '404 - Not Found'

        with open(os.path.join(TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            return file.read()
    
    @staticmethod
    def extract_project(filepath):
        directory = os.path.split(filepath)[0]
    
        with ZipFile(filepath, 'r') as file:
            file.extractall(directory)
        os.unlink(filepath)
    
    def get_functions(self)->list:
        parser = self.lang_parser
        return parser.list_functions() if parser else []
    
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
    def is_private(cls, project_id: str, projects_folder: Path | str = PROJECTS_DIR)-> bool:
        global NOT_FOUND_FILE

        os.chdir(Path(projects_folder, project_id))
        
        if not RunIt.has_config_file():
            return False
        
        project = cls(**RunIt.load_config())
        return project.private

    @classmethod
    async def start(cls, project_id: str, func='index', projects_folder: Path | str = PROJECTS_DIR, args: Optional[Union[dict, list]] = None):
        global NOT_FOUND_FILE

        os.chdir(Path(projects_folder, project_id))

        if not cls.has_config_file():
            return cls.notfound()

        project = cls(**cls.load_config())

        if 'python' in project.runtime:
            project.runtime = cls.PYTHON_PATHS[sys.platform]

        if isinstance(args, dict):
            args = list(args.values())

        args_list = args if isinstance(args, list) else []

        lang_parser = LanguageParser.detect_language(
            filename=project.start_file,
            runtime=project.runtime,
            is_docker=cls.DOCKER,
            project_id=project_id
        )
        
        if not func in lang_parser.functions:
            return RunIt.notfound()
        
        lang_parser.current_func = func
        
        parameters = lang_parser.functions[func] # type: ignore

        try:
            if len(parameters):
                if not len(args_list):
                    raise Exception('[!] No arguments provided')
                return getattr(lang_parser, func)(*args_list)
            else:
                return getattr(lang_parser, func)()
        except AttributeError:
            return cls.notfound()
        except TypeError as e:
            return str(e)
        except Exception as e:
            return str(e)
    
    def serve(self, func: str = 'index', args: Optional[Union[dict,list]]=None):
        global NOT_FOUND_FILE
        
        lang_parser = self.lang_parser
        
        if lang_parser is None:
            return RunIt.notfound()
        
        if func not in lang_parser.functions:
            return RunIt.notfound()
        
        setattr(lang_parser, 'current_func', func)
       
        if isinstance(args, dict):
            args = list(args.values())

        args_list = args if type(args) is list  else []

        parameters = lang_parser.functions[func]

        try:
            if len(parameters):
                if not len(args_list):
                    raise Exception(f'[!] Expected arguments: {parameters}')
                return getattr(lang_parser, func)(*args_list)
            else:
                return getattr(lang_parser, func)()
        except AttributeError as e:
            return RunIt.notfound()
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
        """Get exclude list as a set for O(1) lookups."""
        exclude_set = {self.name + '.zip', '.env', 'account.db', '.git', '.venv', 'venv', 'Dockerfile', '__pycache__'}
        
        if os.path.exists(DOT_RUNIT_IGNORE):
            with open(DOT_RUNIT_IGNORE, 'rt') as file:
                exclude_set.update(os.path.normpath(line.strip()) for line in file if line.strip())
        
        exclude_set.discard('.')
        return exclude_set
    
    def compress(self):
        """Compress project files efficiently."""
        zipname = f'{self.name}.zip'
        exclude_set = self.get_exclude_list()

        def should_exclude(filepath: str) -> bool:
            """Check if file/directory should be excluded."""
            basename = os.path.basename(filepath)
            parts = os.path.normpath(filepath).split(os.sep)
            
            if basename in exclude_set:
                return True
            
            for part in parts:
                if part in exclude_set:
                    return True
            
            return False

        with ZipFile(zipname, 'w') as zipobj:
            logger.info('[!] Compressing Project Files...')
            file_count = 0
            
            for folder_name, subfolders, filenames in os.walk(os.curdir):
                subfolders[:] = [s for s in subfolders if not should_exclude(s)]
                
                for filename in filenames:
                    filepath = os.path.join(folder_name, filename)
                    if not should_exclude(filepath):
                        zipobj.write(filepath, filepath)
                        file_count += 1
            
            logger.info(f'[+] Compressed {file_count} files')
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
        
        self.LANGUAGE_TEMPLATE_FOLDER = Path(TEMPLATES_FOLDER, self.language).resolve()
        self.LANGUAGE_TEMPLATE_FILES = os.listdir(self.LANGUAGE_TEMPLATE_FOLDER)
        
        for template_file in self.LANGUAGE_TEMPLATE_FILES:
            if Path(self.LANGUAGE_TEMPLATE_FOLDER, template_file).resolve().is_file():
                with open(Path(self.LANGUAGE_TEMPLATE_FOLDER, template_file),'rt') as file:
                    with open(Path(os.curdir, self.name, template_file), 'wt') as starter:
                        starter.write(file.read())
            
        with open(Path(TEMPLATES_FOLDER, NOT_FOUND_FILE),'rt') as file:
            with open(Path(os.curdir, self.name, NOT_FOUND_FILE), 'wt') as error_404:
                error_404.write(file.read())
        
        with open(Path(TEMPLATES_FOLDER, DOT_RUNIT_IGNORE),'rt') as file:
            with open(Path(os.curdir, self.name, DOT_RUNIT_IGNORE), 'wt') as dotrunitignore:
                dotrunitignore.write(file.read())
    
    def install_dependency_packages(self):
        global PROJECTS_DIR

        project_path = Path(os.curdir, self.name).resolve()
        
        if RunIt.RUNTIME_ENV != 'server':
            os.chdir(project_path)
        
        # # if project_path != Path(os.curdir).resolve():
        # #     os.chdir(project_path)
        
        packaging_functions = {}
        packaging_functions['javascript'] = self.update_and_install_package_json
        packaging_functions['php'] = self.update_and_install_composer_json
        packaging_functions['python'] = self.install_python_packages
        packaging_functions['multi'] = self.install_all_language_packages
        packaging_functions[self.language]()
    
    def install_all_language_packages(self):
        """Install packages for all languages in parallel."""
        try:
            logger.info("[+] Installing all packages in parallel...")
            
            install_tasks = [
                ('Node.js', self.update_and_install_package_json),
                ('PHP/Composer', self.update_and_install_composer_json),
                ('Python', self.install_python_packages),
            ]
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(task[1]): task[0]
                    for task in install_tasks
                }
                
                for future in as_completed(futures):
                    lang = futures[future]
                    try:
                        future.result()
                        logger.info(f"[+] {lang} packages installed successfully")
                    except Exception as e:
                        logger.warning(f"[!] {lang} package installation failed: {e}")
                        
        except Exception as e:
            logger.warning(f"[!] Package installation error: {e}")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
    
    def update_and_install_package_json(self):
        logger.info("[-] Creating and updating package.json")
        package_file = open('package.json', 'rt')
        package_details = json.load(package_file)
        package_file.close()
        
        package_details['name'] = self.name
        package_details['author'] = self.author
        
        with open('package.json', 'wt') as package_file:
            json.dump(package_details, package_file, indent=4)
        
        try:
            logger.info('[-] Installing node modules...')
            manager = 'bun' if self.runtime == 'bun' else 'npm'
            os.system(f'{manager} install')
        except Exception as e:
            logger.exception(str(e))
            logger.error("[!] Couldn't install modules")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
        

    def update_and_install_composer_json(self):
        logger.info("[-] Creating and updating composer.json")
        
        package_details = {}
        with open('composer.json', 'rt') as package_file:
            package_details = json.load(package_file)
        
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
        venv_path = Path(os.curdir, 'venv').resolve()
        
        if venv_path.exists():
            logger.info(msg="[-] Deleting old virtual environment...")
            rm_command = "rm -rf" if sys.platform != 'win32' else 'rm -r'
            os.system(f"{rm_command} {os.path.realpath(venv_path)}")
        
        logger.info(msg="[!] Creating virtual environment...")
        os.system("python -m venv venv")
        
        pip_path = f"{Path(venv_path, 'bin', 'pip').resolve()}"
        # logger.info(f"--{str(Path(pip_path).resolve())}")
        if sys.platform == 'win32':
            pip_path = Path(venv_path, 'Scripts', 'pip.exe')
        try:
            logger.info("[!] Installing python packages...")
            # os.system(f"{str(pip_path)} install python-dotenv")
            activate_install_instructions = f"""
            {str(pip_path)} install python-dotenv -r requirements.txt
            """.strip()
            os.system(activate_install_instructions)
            logger.info("[+] Installed python packages")
        except Exception as e:
            logger.exception(str(e))
            logger.error("[!] Couldn't install packages")
            logger.debug(INSTALL_MODULE_LATER_MESSAGE)
    

