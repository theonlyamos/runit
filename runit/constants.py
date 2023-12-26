import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VERSION = "0.3.9"
CURRENT_PROJECT = ""
NOT_FOUND_FILE = '404.html'
DOT_RUNIT_IGNORE = '.runitignore'
CONFIG_FILE = 'runit.json'
STARTER_CONFIG_FILE = 'runit.json'
IS_RUNNING = False
CURRENT_PROJECT_DIR = Path(os.curdir).resolve()
RUNIT_HOMEDIR = Path(__file__, '..').resolve()
RUNIT_WORKDIR = os.getenv('RUNIT_WORKDIR', Path(os.path.expanduser('~'), 'RUNIT_WORKDIR'))
TOOLS_DIR = Path(RUNIT_HOMEDIR, 'tools')
PROJECTS_DIR = Path(RUNIT_WORKDIR, 'projects')
TEMPLATES_FOLDER = Path(RUNIT_HOMEDIR, 'templates')
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 9000
API_VERSION = 'v1'

EXT_TO_LOADER = {
    '.py': os.path.join(TOOLS_DIR, 'python', 'loader.py'),
    '.php': os.path.join(TOOLS_DIR, 'php', 'loader.php'),
    '.js': os.path.join(TOOLS_DIR, 'javascript', 'loader.js'),
    '.ts': os.path.join(TOOLS_DIR, 'javascript', 'loader.js'),
}
EXT_TO_RUNNER = {
    '.py': os.path.join(TOOLS_DIR, 'python', 'runner.py'),
    '.php': os.path.join(TOOLS_DIR, 'php', 'runner.php'),
    '.js': os.path.join(TOOLS_DIR, 'javascript', 'runner.js'),
    '.ts': os.path.join(TOOLS_DIR, 'javascript', 'runner.js'),
}
STARTER_FILES = {'python': 'application.py', 
                 'php': 'index.php',
                 'javascript': 'main.js',
                 'multi': 'application.py'}
EXTENSIONS = {'python': '.py',  'php': '.php', 'javascript': '.js'}
EXT_TO_LANG = {'.py': 'python', '.php': 'php', 
               '.js': 'javascript', '.jsx': 'javascript', 
               '.ts': 'javascript', '.tsx': 'javascript'}
LANGUAGE_TO_RUNTIME = {'python': os.getenv('RUNTIME_PYTHON', 'python'), 
                       'php': os.getenv('RUNTIME_PHP', 'php'),
                       'javascript': os.getenv('RUNTIME_JAVASCRIPT', 'node'), 
                       'multi': 'multi'}
EXT_TO_RUNTIME = {'.py': LANGUAGE_TO_RUNTIME['python'], 
                  '.php': LANGUAGE_TO_RUNTIME['php'], 
                  '.js': LANGUAGE_TO_RUNTIME['javascript'],
                  '.ts': LANGUAGE_TO_RUNTIME['javascript']}
BASE_HEADERS = {
    'Content-Type': 'application/json'
}

INSTALL_MODULE_LATER_MESSAGE = '[~] Try again manually later.'
