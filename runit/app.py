#! python3

from flask import Flask, jsonify, redirect, url_for, session, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_restful import Api

from common import Database
from common import FunctionById, FunctionRS, Login, \
    Account, ProjectById, ProjectRS, RunFunction

import os
import logging
from dotenv import load_dotenv, dotenv_values, find_dotenv

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
    
    if 'setup' in settings.keys() and settings['setup'] == 'completed':
        if settings['dbms'] == 'mongodb':
            print('--Connecting to database')
            Database.initialize(app)
    return redirect(url_for('public.index'))

@app.route('/get_app_requests/')
def get_parameters():
    global REQUESTS
    if len(REQUESTS) > 0:
        return jsonify(REQUESTS.pop())
    return jsonify({'GET': {}, 'POST': {}})

from blueprints import public, account, functions, project, admin, setup

app.register_blueprint(setup)
app.register_blueprint(public)
app.register_blueprint(functions)
app.register_blueprint(account)
app.register_blueprint(project)

app.register_blueprint(admin, subdomain='admin')

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

if __name__ == "__main__":
    app.run(debug=True, port=9000)
