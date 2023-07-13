import os
from datetime import datetime, timedelta
from subprocess import check_output

from dotenv import load_dotenv
from ..constants import EXT_TO_RUNTIME

load_dotenv()

class Runtime(object):
    '''
    Class for parsing and running
    functions from file
    '''
    LOADER = ""
    RUNNER = ""
    
    def __init__(self, filename="", runtime="", is_file = False, is_docker=False, project_id=''):
        extension = os.path.splitext(filename)[1].lower()
        self.filename = filename
        self.runtime = runtime
        self.is_file = is_file
        self.is_docker = is_docker
        self.project_id = project_id
        self.module = os.path.realpath(os.path.join(os.curdir, self.filename))
        self.functions = []
        self.load_functions_from_supported_files()
    
    def load_functions_from_supported_files(self):
        '''
        Class method for loading exported
        function names in .js file

        @param None
        @return None
        '''
        
        try:
            if self.is_docker:
                import docker
                client = docker.from_env()

                print(f"{self.project_id} {self.LOADER} {self.module}")
                result = client.containers.run(self.project_id, f'{self.LOADER} {self.module}', auto_remove=True)
                print(result)
            else:
                result = check_output(f'{self.runtime} {self.LOADER} {self.module}', shell=True, encoding='utf-8')
            result = result.strip()
            if self.runtime == 'php':
                self.functions = result.split(',')
            else:
                self.functions = eval(result)

            for key in self.functions:
                self.__setattr__(key, self.anon_function)
                
        except Exception as e:
            print(str(e))
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
                    return os.system(f'{self.runtime} {self.filename} "{args}"')
                else:
                    result = check_output(f'{self.runtime} {self.RUNNER} {self.module} {self.current_func} "{args}"', shell=True, encoding='utf-8')
            else:
                if self.is_file:
                    return os.system(f'{self.runtime} {self.filename}')
                else:
                    result = check_output(f'{self.runtime} {self.RUNNER} {self.module} {self.current_func}', shell=True, encoding='utf-8')

            return result.strip()
        except Exception as e:
            return str(e)