from typing import Type
from .python import Python
from .php import PHP
from .javascript import Javascript

import os
from typing import Union

class LanguageParser(object):
    '''
    Class for parsing script language.
    Determines which language paackage
    to use
    '''

    EXT_TO_LANG = {'.py': Python, '.php': PHP, '.js': Javascript,
                   '.jsx': Javascript, '.ts': Javascript, '.tsx': Javascript}

    def __init__(self):
        pass
    
    @staticmethod
    def detect_language(filename: str, runtime: str)-> Union[Python, PHP, Javascript]:
        return LanguageParser.EXT_TO_LANG[os.path.splitext(filename)[1].lower()](filename, runtime)

    @staticmethod
    def run_file(filename, runtime):
        lang_parser = LanguageParser.detect_language(filename, runtime)
        lang_parser.is_file = True
        lang_parser.anon_function()
