#! python

from flask import Flask, jsonify, redirect, url_for, session, request
from flask_jwt_extended import JWTManager
from flask_restful import Api

from common import Database
from common import FunctionById, FunctionRS, Login, \
    Account, ProjectById, ProjectRS, RunFunction

from models import Admin
from models import Role

import os
import logging
from dotenv import load_dotenv, dotenv_values, find_dotenv, set_key

app = Flask(__name__)
api = Api(app, prefix='/api')

load_dotenv()
app.secret_key =  os.getenv('RUNIT_SECRET_KEY')
app.config['SERVER_NAME'] = os.getenv('RUNIT_SERVERNAME')

jwt = JWTManager(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

REQUESTS = []

#api.add_resource(RunFunction, '/<string:project_id>/<string:function>/')
api.add_resource(Login, '/login/')
api.add_resource(Account, '/account/')
api.add_resource(ProjectRS, '/projects/')
api.add_resource(ProjectById, '/projects/<string:project_id>/')
#api.add_resource(RunFunction, '/<string:project_id>/<string:function>/')
#api.add_resource(FunctionRS, '/functions/')
#api.add_resource(FunctionById, '/functions/<string:function_id>/')

@app.route('/complete_setup/')
def complete_setup():
    global app
    settings = dotenv_values(find_dotenv())
    print('--Setting up database')
    Database.initialize(settings, app)

    if 'setup' in settings.keys() and settings['setup'] == 'completed':
        if settings['dbms'] == 'mysql':
            Database.setup()
            print('[--] Database setup complete')
    if not Role.count():
        print('[#] Populating Roles')
        Role('developer', []).save()
        Role('superadmin', []).save()
        Role('subadmin', []).save()
    if not Admin.count():
        print('[#] Creating default administrator')
        Admin('Administrator', settings['adminusername'], settings['adminpassword'], 1).save()
    
    del settings['adminusername']
    del settings['adminpassword']

    env_file = find_dotenv()
    file = open(env_file, 'w')
    file.close()

    for key, value in settings.items():
        set_key(env_file, key, value)

    return redirect(url_for('public.index'))

@app.route('/get_app_requests/')
def get_parameters():
    global REQUESTS
    if len(REQUESTS) > 0:
        return jsonify(REQUESTS.pop())
    return jsonify({'GET': {}, 'POST': {}})

@app.before_first_request
def init():
    global app

    settings = dotenv_values(find_dotenv())
    
    if 'setup' in settings.keys() and settings['setup'] == 'completed':
        Database.initialize(settings, app)
    if not (os.path.exists(os.path.join(os.curdir, 'accounts'))):
        os.mkdir(os.path.join(os.curdir, 'accounts'))
    if not (os.path.exists(os.path.join(os.curdir, 'projects'))):
        os.mkdir(os.path.join(os.curdir, 'projects'))

@app.before_request
def startup():
    # if not os.path.exists('.env'):
    #     with open('.env', 'wt') as file:
    #         file.close()
    #     return redirect(url_for('setup.index'))
    global REQUESTS
    if request.path != '/get_app_requests/':
        REQUESTS.insert(0, 
                        {'GET': request.args.to_dict(),
                        'POST': request.form.to_dict()})

from blueprints import public, account, functions, project, admin, setup

app.register_blueprint(setup)
app.register_blueprint(public)
app.register_blueprint(functions)
app.register_blueprint(account)
app.register_blueprint(project)
app.register_blueprint(admin, subdomain='admin')

if __name__ == "__main__":
    app.run(debug=True, port=9000)
