import os
import sys
import inspect

functions = {}
try:
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filepath = os.path.split(filename)[0]

        sys.path.append(filepath)
        module = __import__(str(inspect.getmodulename(filename)))
        methods = [f[1] for f in inspect.getmembers(module, inspect.isfunction)]
        
        for func in methods:
            sig = inspect.signature(func)
            params = sig.parameters
            
            functions[func.__name__] =  list(params.keys())
            
    print(functions)
except Exception as e:
    print(str(e))
