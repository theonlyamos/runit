import os
import sys
import inspect
from dotenv import load_dotenv

args = sys.argv
functionArguments = None

try:
    if len(args) >= 3:
        filename = args[1]
        functionname = args[2]
        filepath = os.path.split(filename)[0]
        load_dotenv(os.path.join(filepath, '.env'))
        sys.path.append(filepath)
        module = __import__(inspect.getmodulename(filename))
        method = [f[1] for f in inspect.getmembers(module, inspect.isfunction) if f[0] == functionname][0]

        if len(args) > 3:
            functionArguments = args[3]

        if functionArguments is not None:
            method(functionArguments)
        else:
            method()
    
except Exception as e:
    print(str(e))