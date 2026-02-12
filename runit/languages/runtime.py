import os
import ast
import time
import subprocess
from typing import Callable
from datetime import datetime, timedelta

from dotenv import load_dotenv
from ..constants import EXT_TO_RUNTIME

load_dotenv()

class Runtime():
    '''
    Class for parsing and running
    functions from file
    '''
    LOADER = ""
    RUNNER = ""
    _function_cache = {}
    _cache_ttl = 300
    
    def __init__(self, filename="", runtime="", is_file = False, is_docker=False, project_id=''):
        self.filename = filename
        self.iruntime = runtime
        self.is_file = is_file
        self.is_docker = is_docker
        self.project_id = project_id
        self.module = os.path.realpath(os.path.join(os.curdir, self.filename))
        self.functions = {}
        self.current_func: str = 'index'
        self.load_functions_from_supported_files()
    
    def load_functions_from_supported_files(self):
        '''
        Class method for loading exported
        function names in application files

        @param None
        @return None
        '''
        
        try:
            if os.path.exists(self.module):
                mtime = os.path.getmtime(self.module)
                cache_key = (self.module, mtime)
                
                if cache_key in Runtime._function_cache:
                    cached_data = Runtime._function_cache[cache_key]
                    if time.time() - cached_data['timestamp'] < Runtime._cache_ttl:
                        self.functions = cached_data['functions']
                        for key in self.functions.keys():
                            self.__setattr__(key, self.anon_function)
                        return
            
            if self.is_docker:
                import docker
                client = docker.from_env()

                result = client.containers.run(self.project_id, [self.LOADER, self.module], auto_remove=True)
            else:
                result = subprocess.run(
                    [self.iruntime, self.LOADER, self.module],
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout
            
            result = str(result).strip()
            
            self.functions = ast.literal_eval(result)
            
            if os.path.exists(self.module):
                mtime = os.path.getmtime(self.module)
                cache_key = (self.module, mtime)
                Runtime._function_cache[cache_key] = {
                    'functions': self.functions,
                    'timestamp': time.time()
                }
            
            for key in self.functions.keys():
                self.__setattr__(key, self.anon_function)
                
        except Exception as e:
            return str(e)
        
    def list_functions(self):
        '''
        List Class methods

        @param None
        @retun None
        '''
        return [func for func in self.functions]

    def anon_function(self, *args):
        args_str = ', '.join(args)
        try:
            if len(args):
                if self.is_file:
                    return subprocess.run(
                        [self.iruntime, self.filename, args_str],
                        check=True
                    ).returncode
                else:
                    result = subprocess.run(
                        [self.iruntime, self.RUNNER, self.module, self.current_func, args_str],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout
            else:
                if self.is_file:
                    return subprocess.run(
                        [self.iruntime, self.filename],
                        check=True
                    ).returncode
                else:
                    result = subprocess.run(
                        [self.iruntime, self.RUNNER, self.module, self.current_func],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout

            return result.strip()
        except subprocess.CalledProcessError as e:
            return e.stderr if e.stderr else str(e)
        except Exception as e:
            return str(e)
