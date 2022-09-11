from datetime import datetime, timedelta
import os
from subprocess import check_output
from typing import Any

PHP_TOOLS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','tools', 'php')
LOADER = os.path.realpath(os.path.join(PHP_TOOLS_DIR, 'loader.php'))
RUNNER = os.path.realpath(os.path.join(PHP_TOOLS_DIR, 'runner.php'))

class PHP(object):
    '''
    Class for parsing and running php
    functions from file
    '''
    def __init__(self, filename):
        self.filename = filename
        self.module = os.path.realpath(os.path.join(os.curdir, self.filename))
        self.functions = []
        self.load_functions_from_file()
    
    def load_functions_from_file(self):
        '''
        Class method for retrieving exported
        function names in .php file

        @param None
        @return None
        '''
        
        try:
            command = check_output(f'php {LOADER} {self.module}', shell=True)
            result = str(command)
            result = result.lstrip("b'").lstrip('"').replace('\\n', '\n').replace('\\r', '\r').rstrip("'").rstrip('"').strip()
            self.functions = result.split(',')

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
                command = check_output(f'php {RUNNER} {self.module} {self.current_func} "{args}"', shell=True)
            else:
                command = check_output(f'php {RUNNER} {self.module} {self.current_func}', shell=True)

            result = str(command)
            return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'").strip()
        except Exception as e:
            return str(e)

    '''
    def anon_function(self, *args):
        func = self.functions[self.current_func]
        if len(args) != len(func['args']):
            raise TypeError(f'TypeError: {len(func["args"])} positional argument(s) required, but {len(args)} were given!')
        arguments = {}
        if len(args):
            for arg in range(0, len(func['args'])):
                arguments[func['args'][arg]] = args[arg]

        if type(func['code']) == tuple:
            func['code'] = ''.join(func['code'])
        
        code = '<?php\n'
        
        if '$_GET' in func['code'] or '$_POST' in func['code'] or \
            '$_REQUEST' in func['code'] or '$_SERVER' in func['code']:
            code += 'require_once "./request.php"\n'
        code += func['code']
        code += f'{func["name"]}('
        for c in args:
            code += f'"{c}",'
        code += ')'
        code += '\n?>'

        tempfile = f'.tmp_{self.current_func}_{datetime.utcnow().strftime("%s")}.php'
        with open(tempfile, 'wt') as file:
            print(code, file=file)
        
        command = check_output(f'php {tempfile}', shell=True)
        os.unlink(tempfile)
        result = str(command)
        return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'").strip()
    '''
