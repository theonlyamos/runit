from flask import Blueprint, request
from runit import RunIt
import os

account = Blueprint('account', __name__)

@account.before_request
def get_subdomain():
    print(request.host)
    #print(g.subdomain)
    return

@account.route('/')
def index(subdomain):
    print(f"[1] {subdomain}")
    return 'Hello World'

@account.route('/<page>')
def main(subdomain, page):
    if (os.path.isdir(os.path.join('accounts', page))):
        os.chdir(os.path.join('accounts', page))
        result = RunIt.start()
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()