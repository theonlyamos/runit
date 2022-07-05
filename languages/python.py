import os
import sys
import inspect

class Python(object):
    '''
    Class for parsing python files
    Only supports Python 3
    '''
    def __init__(self, filename):
        self.filename = filename
        self.import_file_as_module()
        #print([f for f in inspect.getmembers(self, inspect.isfunction)])
    
    def import_file_as_module(self):
        sys.path.append(os.path.abspath(os.curdir))
        module = __import__(inspect.getmodulename(self.filename))
        functions = [f for f in inspect.getmembers(module, inspect.isfunction)]

        for func in functions:
            setattr(self, func[0], func[1])
    
    def list_functions(self):
        return [f[0] for f in inspect.getmembers(self, inspect.isfunction)]