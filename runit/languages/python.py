import os
from .runtime import Runtime

PY_TOOLS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', 'tools', 'python')

class Python(Runtime):
    '''
    Class for parsing and running
    python functions from file
    '''
    LOADER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'loader.py'))
    RUNNER = os.path.realpath(os.path.join(PY_TOOLS_DIR, 'runner.py'))

    def __init__(self, filename, runtime, is_file=False, is_docker=False, project_id=''):
        super().__init__(filename, runtime, is_file, is_docker, project_id)