import os
import sys
import ast
import time
import inspect
import asyncio
import importlib.util
from typing import Callable, Dict, Any, Optional

from .runtime import Runtime

PY_TOOLS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'tools', 'python')

class Python(Runtime):
    '''
    Class for parsing and running Python functions from file
    with in-memory execution for improved performance.
    '''
    LOADER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'loader.py'))
    RUNNER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'runner.py'))
    
    _module_cache: Dict[str, Any] = {}
    _module_mtimes: Dict[str, float] = {}

    def __init__(self, filename, runtime, is_file=False, is_docker=False, project_id=''):
        self._loaded_module = None
        self._loaded_functions: Dict[str, Callable] = {}
        self.module = os.path.realpath(os.path.join(os.curdir, filename))
        
        if not is_file and not is_docker:
            self._load_module_in_memory()
        
        super().__init__(filename, runtime, is_file, is_docker, project_id)

    def _load_module_in_memory(self):
        """Load the Python module directly into memory for faster execution."""
        if not os.path.exists(self.module):
            return
            
        try:
            mtime = os.path.getmtime(self.module)
            module_key = self.module
            
            if module_key in Python._module_cache:
                cached_mtime = Python._module_mtimes.get(module_key, 0)
                if mtime == cached_mtime:
                    self._loaded_module = Python._module_cache[module_key]
                    self._extract_functions_from_module()
                    return
            
            spec = importlib.util.spec_from_file_location("runit_module", self.module)
            if spec and spec.loader:
                self._loaded_module = importlib.util.module_from_spec(spec)
                sys.modules["runit_module"] = self._loaded_module
                
                filepath = os.path.split(self.module)[0]
                if filepath not in sys.path:
                    sys.path.insert(0, filepath)
                
                spec.loader.exec_module(self._loaded_module)
                
                Python._module_cache[module_key] = self._loaded_module
                Python._module_mtimes[module_key] = mtime
                
                self._extract_functions_from_module()
        except Exception as e:
            pass

    def _extract_functions_from_module(self):
        """Extract callable functions from the loaded module."""
        if self._loaded_module is None:
            return
            
        for name, obj in inspect.getmembers(self._loaded_module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                self._loaded_functions[name] = obj

    def load_functions_from_supported_files(self):
        """Load function metadata, using in-memory module if available."""
        try:
            if self._loaded_functions:
                self.functions = {name: list(inspect.signature(func).parameters.keys()) 
                                 for name, func in self._loaded_functions.items()}
            else:
                super().load_functions_from_supported_files()
            
            for key in self.functions.keys():
                self.__setattr__(key, self.anon_function)
        except Exception as e:
            return str(e)

    def anon_function(self, *args):
        """Execute function in-memory if available, otherwise fall back to subprocess."""
        func_name = self.current_func
        
        if func_name in self._loaded_functions:
            return self._execute_in_memory(func_name, *args)
        
        return super().anon_function(*args)

    def _execute_in_memory(self, func_name: str, *args):
        """Execute a function directly in memory."""
        try:
            func = self._loaded_functions[func_name]
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            if asyncio.iscoroutinefunction(func):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if len(params) and args:
                        result = loop.run_until_complete(func(*args))
                    else:
                        result = loop.run_until_complete(func())
                finally:
                    loop.close()
            else:
                if len(params) and args:
                    result = func(*args)
                else:
                    result = func()
            
            return result
        except Exception as e:
            return str(e)

    async def anon_function_async(self, *args):
        """Async version for use in async web servers."""
        func_name = self.current_func
        
        if func_name in self._loaded_functions:
            return await self._execute_in_memory_async(func_name, *args)
        
        return self.anon_function(*args)

    async def _execute_in_memory_async(self, func_name: str, *args):
        """Execute a function in memory, handling async functions properly."""
        try:
            func = self._loaded_functions[func_name]
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            if asyncio.iscoroutinefunction(func):
                if len(params) and args:
                    result = await func(*args)
                else:
                    result = await func()
            else:
                if len(params) and args:
                    result = func(*args)
                else:
                    result = func()
            
            return result
        except Exception as e:
            return str(e)
