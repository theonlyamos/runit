from flask import Flask, request, jsonify
from blueprints.account import account
from blueprints.public import public
import uuid
import os

REQUESTS = []

app = Flask(__name__)

app.secret = uuid.uuid4()
app.config['SERVER_NAME'] = 'localhost:9000'

@app.before_first_request
def init():
    if not (os.path.exists(os.path.join(os.curdir, 'accounts'))):
        os.mkdir(os.path.join(os.curdir, 'accounts'))

@app.before_request
def populate():
    global REQUESTS
    if request.path != '/get_app_requests/':
        REQUESTS.insert(0, 
                        {'GET': request.args.to_dict(),
                        'POST': request.form.to_dict()})

@app.route('/')
def index():
    return "Hello World"

@app.route('/get_app_requests/')
def get_parameters():
    global REQUESTS
    if len(REQUESTS) > 0:
        return jsonify(REQUESTS.pop())
    return jsonify({'GET': {}, 'POST': {}})

app.register_blueprint(public)
app.register_blueprint(account, subdomain="<subdomain>")

if __name__ == "__main__":
    app.run(debug=True, port=9000)
