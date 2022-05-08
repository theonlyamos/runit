from flask import Blueprint, request
from runit import RunIt
import os

public = Blueprint('public', __name__)

@public.before_request
def initial():
    os.chdir("/home/void/Dev/python/runit")

@public.route('/')
def index():
    return 'Index Page'

@public.route('/login', methods=['GET', 'POST'])
def login():
    return 'Login Page'

@public.route('/register', methods=['GET', 'POST'])
def register():
    return 'Registration Page'

@public.route('/<account>/', methods=['GET','POST','PUT','PATCH','DELETE'])
def main(account):
    if (os.path.isdir(os.path.join('accounts', account))):
        result = RunIt.start(account)
        return result
    else:
        return RunIt.notfound()

@public.route('/<account>/<page>/', methods=['GET','POST','PUT','PATCH','DELETE'])
def page(account, page='index'):
    if (os.path.isdir(os.path.join('accounts', account))):
        result = RunIt.start(account, page)
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()