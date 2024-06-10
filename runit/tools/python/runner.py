import os
import sys
import inspect
import asyncio
from dotenv import load_dotenv

args = sys.argv
functionArguments = None

async def run_async_function(async_func, *args):
    return await async_func(*args)

try:
    if len(args) >= 3:
        filename = args[1]
        functionname = args[2]
        filepath = os.path.split(filename)[0]
        filepath = os.path.split(filename)[0]
        env_path = os.path.join(filepath, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        sys.path.append(filepath)
        module = __import__(str(inspect.getmodulename(filename)))
        method = [f[1] for f in inspect.getmembers(module, inspect.isfunction) if f[0] == functionname][0]
        
        sig = inspect.signature(method)
        params = sig.parameters
        
        if len(args) > 3:
            functionArguments = args[3]
        
        if len(params.keys()) and functionArguments:
            if asyncio.iscoroutinefunction(method):
                result = asyncio.run(run_async_function(method, functionArguments))
            else:
                result = method(functionArguments)
        else:
            if asyncio.iscoroutinefunction(method):
                result = asyncio.run(run_async_function(method))
            else:
                result = method()
        print(result)          
except Exception as e:
    print(str(e))