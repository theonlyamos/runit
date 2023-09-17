from typing import Type
from .php import PHP
from .multi import Multi
from .python import Python
from .javascript import Javascript

import os
from typing import Union

class LanguageParser():
    '''
    Class for parsing script language.
    Determines which language paackage
    to use
    '''

    EXT_TO_LANG = {'.py': Python, '.php': PHP, '.js': Javascript,
                   '.jsx': Javascript, '.ts': Javascript, '.tsx': Javascript}
    
    @staticmethod
    def detect_language(filename: str, runtime: str, is_file: bool = False, is_docker: bool = False, project_id: str = '')-> Union[Python, PHP, Javascript, Multi]:
        if runtime == 'multi':
            return Multi(filename, runtime, is_file, is_docker, project_id)
        return LanguageParser.EXT_TO_LANG[os.path.splitext(filename)[1].lower()](
            filename, 
            runtime,
            is_file,
            is_docker,
            project_id
        )

    @staticmethod
    def run_file(filename, runtime):
        lang_parser = LanguageParser.detect_language(filename, runtime, True)
        lang_parser.is_file = True
        lang_parser.anon_function()
