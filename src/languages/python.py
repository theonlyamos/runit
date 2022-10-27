from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from subprocess import check_output
from typing import Any

load_dotenv()

PY_TOOLS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', 'tools', 'python')
LOADER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'loader.py'))
RUNNER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'runner.py'))

class Python(object):
    '''
    Class for parsing and running
    Javascript functions from file
    '''
    def __init__(self, filename, runtime):
        self.filename = filename
        self.runtime = runtime
        self.module = os.path.realpath(os.path.join(os.curdir, self.filename))
        self.functions = []
        self.load_functions_from_file()
    
    def load_functions_from_file(self):
        '''
        Class method for retrieving exported
        function names in .js file

        @param None
        @return None
        '''
        
        try:
            command = check_output(f'{self.runtime} {LOADER} {self.module}', shell=True)
            result = str(command)
            result = result.lstrip("b'").lstrip('"').replace('\\n', '\n').replace('\\r', '\r').rstrip("'").rstrip('"')
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
                command = check_output(f'{self.runtime} {RUNNER} {self.module} {self.current_func} "{args}"', shell=True)
            else:
                command = check_output(f'{self.runtime} {RUNNER} {self.module} {self.current_func}', shell=True)

            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'").strip()
        except Exception as e:
            return str(e)