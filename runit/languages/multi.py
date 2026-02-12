import os
import ast
import json
import subprocess

from ..constants import EXT_TO_RUNTIME, EXT_TO_LOADER, EXT_TO_RUNNER
from .runtime import Runtime

MULTI_TOOLS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', 'tools', 'multi')

class Multi(Runtime):
    '''
    Class for parsing and running
    python functions from file
    '''
    LOADER = os.path.realpath(os.path.join(MULTI_TOOLS_DIR, 'loader.py'))
    RUNNER = os.path.realpath(os.path.join(MULTI_TOOLS_DIR, 'runner.py'))

    def __init__(self, filename, runtime, is_file, is_docker, project_id):
        super().__init__(filename, runtime, is_file, is_docker, project_id)
    
    def load_files(self)-> list[str]:
        '''
        Class method for loading file list
        of supported files in project directory
        
        @param None
        @return list List of files
        '''
        return [sfile for sfile in os.listdir(os.curdir) if os.path.splitext(sfile)[1].lower() in EXT_TO_RUNTIME.keys()]
    
    def load_functions_from_supported_files(self):
        '''
        Class method for loading exported
        function names from all supported files 
        types

        @param None
        @return None
        '''
        
        try:
            self.functions = {}
            files = self.load_files()
            for lfile in files:
                try:
                    extension = os.path.splitext(lfile)[1].lower()
                    loader = EXT_TO_LOADER[extension]
                    runner = EXT_TO_RUNNER[extension]
                    runtime = EXT_TO_RUNTIME[extension]

                    full_path = os.path.join(os.path.realpath(os.curdir), lfile)
                    result = subprocess.run(
                        [runtime, loader, full_path],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout
                    result = result.strip()
                    
                    if extension == '.php':
                        loaded_functions = result.split(',')
                    elif extension == '.js':
                        loaded_functions = json.loads(result)
                    else:
                        loaded_functions = ast.literal_eval(result)
                    
                    for func in loaded_functions:
                        self.functions[func] = {
                            'runtime': runtime,
                            'loader': loader,
                            'runner': runner,
                            'module': full_path
                        }
                
                except Exception as e:
                    continue
            
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
        return [func for func in self.functions.keys()]
    
    def anon_function(self, *args):
        args_str = ', '.join(args)
        try:
            loaded_function = self.functions[self.current_func]
            runtime = loaded_function['runtime']
            runner = loaded_function['runner']
            module = loaded_function['module']
            
            if len(args_str):
                result = subprocess.run(
                    [runtime, runner, module, self.current_func, args_str],
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout
            else:
                result = subprocess.run(
                    [runtime, runner, module, self.current_func],
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout

            return result.strip()
        except subprocess.CalledProcessError as e:
            return e.stderr if e.stderr else str(e)
        except Exception as e:
            return str(e)
