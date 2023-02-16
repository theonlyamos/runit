import os
from dotenv import load_dotenv

load_dotenv()

VERSION = "0.0.9"
CURRENT_PROJECT = ""
TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
STARTER_FILES = {'python': 'application.py', 'php': 'index.php','javascript': 'main.js'}
EXTENSIONS = {'python': '.py',  'php': '.php', 'javascript': '.js'}
EXT_TO_LANG = {'.py': 'python', '.php': 'php', '.js': 'javascript',
               '.jsx': 'javascript', '.ts': 'javascript', '.tsx': 'javascript'}
EXT_TO_RUNTIME = {'.py': os.getenv('RUNTIME_PYTHON', 'python'), 
                  '.php': os.getenv('RUNTIME_PHP', 'php'), 
                  '.js': os.getenv('RUNTIME_JAVASCRIPT', 'node'),
                  '.jsx': os.getenv('RUNTIME_JAVASCRIPT', 'node'),
                  '.ts': os.getenv('RUNTIME_JAVASCRIPT', 'node'),
                  '.tsx': os.getenv('RUNTIME_JAVASCRIPT', 'node')}
LANGUAGE_TO_RUNTIME = {'python': 'python', 'php': 'php',
                  'javascript': 'node'}
NOT_FOUND_FILE = '404.html'
CONFIG_FILE = 'runit.json'
STARTER_CONFIG_FILE = 'runit.json'
IS_RUNNING = False
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'projects')
CURRENT_PROJECT_DIR = os.path.realpath(os.curdir)
BASE_HEADERS = {
    'Content-Type': 'application/json'
}
