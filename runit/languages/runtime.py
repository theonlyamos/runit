import os
from typing import Callable
from datetime import datetime, timedelta
from subprocess import check_output

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
    
    def __init__(self, filename="", runtime="", is_file = False, is_docker=False, project_id=''):
        # extension = os.path.splitext(filename)[1].lower()
        self.filename = filename
        self.iruntime = runtime
        self.is_file = is_file
        self.is_docker = is_docker
        self.project_id = project_id
        self.module = os.path.realpath(os.path.join(os.curdir, self.filename))
        self.functions = []
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
            if self.is_docker:
                import docker
                client = docker.from_env()

                result = client.containers.run(self.project_id, f'{self.LOADER} {self.module}', auto_remove=True)
            else:
                result = check_output(f'{self.iruntime} {self.LOADER} {self.module}', shell=True, encoding='utf-8')
            
            result = str(result).strip()
            
            if self.iruntime == 'php':
                self.functions = result.split(',')
            else:
                self.functions = eval(result)

            for key in self.functions:
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
        args = ', '.join(args)
        try:
            if len(args):
                if self.is_file:
                    return os.system(f'{self.iruntime} {self.filename} "{args}"')
                else:
                    result = check_output(f'{self.iruntime} {self.RUNNER} {self.module} {self.current_func} "{args}"', shell=True, encoding='utf-8')
            else:
                if self.is_file:
                    return os.system(f'{self.iruntime} {self.filename}')
                else:
                    result = check_output(f'{self.iruntime} {self.RUNNER} {self.module} {self.current_func}', shell=True, encoding='utf-8')

            return result.strip()
        except Exception as e:
            return str(e)