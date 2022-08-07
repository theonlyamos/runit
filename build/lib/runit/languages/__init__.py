from .python import Python
from .php import PHP
from .javascript import Javascript

import os

class LanguageParser(object):
    '''
    Class for parsing script language.
    Determines which language paackage
    to use
    '''

    EXT_TO_LANG = {'.py': Python, '.php': PHP, '.js': Javascript}

    def __init__(self):
        pass
    
    @staticmethod
    def detect_language(filename: str)-> object:
        return LanguageParser.EXT_TO_LANG[os.path.splitext(filename)[1].lower()](filename)
