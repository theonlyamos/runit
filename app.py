from flask import Flask, jsonify, session, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_restful import Api

from common.database import Database
from common.apis import FunctionById, FunctionRS, Login, \
    Account, ProjectById, ProjectRS, RunFunction

import os
import logging

app = Flask(__name__)
api = Api(app, prefix='/api')

app.secret_key =  os.getenv('RUNIT_SECRET_KEY')
app.config['SERVER_NAME'] = os.getenv('RUNIT_SERVERNAME')

jwt = JWTManager(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

REQUESTS = []
MENU = [
    {'name': 'home', 'icon': 'home', 'url': 'account.index'},
    {'name': 'projects', 'icon': 'th-large', 'url': 'account.projects'},
    {'name': 'functions', 'icon': 'terminal', 'url': 'account.functions'},
    {'name': 'profile', 'icon': 'user', 'url': 'account.profile'}
]

@app.before_first_request
def init():
    global MENU
    global app
    session['menu'] = MENU
    #session.clear()
    Database.initialize(app)
    if not (os.path.exists(os.path.join(os.curdir, 'accounts'))):
        os.mkdir(os.path.join(os.curdir, 'accounts'))
    if not (os.path.exists(os.path.join(os.curdir, 'projects'))):
        os.mkdir(os.path.join(os.curdir, 'projects'))

@app.before_request
def populate():
    global REQUESTS
    if request.path != '/get_app_requests/':
        REQUESTS.insert(0, 
                        {'GET': request.args.to_dict(),
                        'POST': request.form.to_dict()})

#api.add_resource(RunFunction, '/<string:project_id>/<string:function>/')
api.add_resource(Login, '/login/')
api.add_resource(Account, '/account/')
api.add_resource(ProjectRS, '/projects/')
api.add_resource(ProjectById, '/projects/<string:project_id>/')
#api.add_resource(RunFunction, '/<string:project_id>/<string:function>/')
#api.add_resource(FunctionRS, '/functions/')
#api.add_resource(FunctionById, '/functions/<string:function_id>/')

@app.route('/get_app_requests/')
def get_parameters():
    global REQUESTS
    if len(REQUESTS) > 0:
        return jsonify(REQUESTS.pop())
    return jsonify({'GET': {}, 'POST': {}})

from blueprints import public, account, functions

app.register_blueprint(public)
app.register_blueprint(functions)
app.register_blueprint(account)

#app.register_blueprint(account, subdomain='account')

if __name__ == "__main__":
    app.run(debug=True, port=9000)
