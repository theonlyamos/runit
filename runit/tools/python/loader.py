import os
import sys
import inspect
from dotenv import load_dotenv

try:
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filepath = os.path.split(filename)[0]
        load_dotenv(os.path.join(filepath, '.env'))
        sys.path.append(filepath)
        module = __import__(inspect.getmodulename(filename))
        functions = [f[0] for f in inspect.getmembers(module, inspect.isfunction)]
        print(functions)
    
except Exception as e:
    print(str(e))
