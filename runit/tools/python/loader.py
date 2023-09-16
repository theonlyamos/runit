import os
import sys
import inspect

try:
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filepath = os.path.split(filename)[0]
        sys.path.append(filepath)
        module = __import__(inspect.getmodulename(filename))
        functions = [f[0] for f in inspect.getmembers(module, inspect.isfunction)]
        print(functions)
    
except Exception as e:
    print(str(e))
