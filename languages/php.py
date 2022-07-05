from datetime import datetime, timedelta
import os
from subprocess import check_output
from typing import Any

class PHP(object):
    '''
    Class for parsing and running php
    functions from file
    '''
    def __init__(self, filename):
        self.filename = filename
        self.functions = {}
        self.load_functions_from_file()
    
    def load_functions_from_file(self):
        with open(self.filename, 'rt') as file:
            lines = file.readlines()
            lines = [l for l in lines if l.strip() != '?>'] 
            if not lines[-1].strip():
                del lines[-1]

        array = []

        for line in range(0, len(lines)):
            if 'function' in lines[line]:
                name = lines[line].strip().split(' ')[1].split('(')[0]
                args = lines[line].strip().split('(')[1].split(')')[0].split(',')
                args = [a.replace('$', '') for a in args]
                args = [a for a in args if a]
                self.functions[name] = {'name': name, 'args': args}
                
                if lines[line].rstrip().endswith('{'):
                    array.append([line, lines[line].lstrip(), 1])
                else:
                    array.append([line, lines[line].lstrip().rstrip('\n')+'{\n', 0])
        
        for arr in range(0, len(array)):
            key = array[arr][1].strip().split(' ')[1].split('(')[0]
            if arr < len(array)-1:
                if array[arr][2]:
                    self.functions[key]['code'] = array[arr][1]+''.join([r for r in
                        lines[array[arr][0]+1:array[arr+1][0]-1]])
                else:
                    self.functions[key]['code'] = array[arr][1]+''.join([r for r in
                        lines[array[arr][0]+2:array[arr+1][0]-1]])
            else:
                if array[arr][2]:
                    self.functions[key]['code'] =  array[arr][1]+''.join([r for r in lines[array[arr][0]+1:]])
                else:
                    self.functions[key]['code'] = array[arr][1],''.join([r for r in lines[array[arr][0]+2:]])

        for key in self.functions.keys():
            self.__setattr__(key, self.anon_function)
    
    def list_functions(self):
        return [func for func in self.functions.keys()]

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
        return result.lstrip("b'").replace('\\n', '\n').replace('\\r', '\r').rstrip("'")