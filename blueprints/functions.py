from crypt import methods
from flask import Blueprint, request
from models.project import Project
from runit import RunIt
import os

functions = Blueprint('functions', __name__)

@functions.get('/<string:project_id>/<string:function>/')
def run(project_id, function_name):
    if (os.path.isdir(os.getenv('RUNIT_HOMEDIR')+project_id)):
        #os.chdir(project.path)
        result = RunIt.start(project_id, function_name)
        #os.chdir(os.path.join('..', '..'))
        return result

    return RunIt.notfound()