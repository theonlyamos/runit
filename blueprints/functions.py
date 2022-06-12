from flask import Blueprint, request
from runit import RunIt
import os

functions = Blueprint('functions', __name__)

@functions.before_request
def get_subdomain():
    print(request.host)
    #print(g.subdomain)
    return

@functions.route('/')
def index(subdomain):
    print(f"[1] {subdomain}")
    return 'Hello World'

@functions.route('/<page>')
def main(subdomain, page):
    if (os.path.isdir(os.path.join('functionss', page))):
        os.chdir(os.path.join('functionss', page))
        result = RunIt.start()
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()