import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import uvicorn
import sys
from pathlib import Path
from dotenv import find_dotenv, dotenv_values, set_key
from .constants import (
    RUNIT_HOMEDIR, SERVER_HOST, SERVER_PORT
)

class RunitServerSetup:
    @staticmethod
    def create_default_env_file():
        if not find_dotenv():
            env_path = Path(RUNIT_HOMEDIR) / '.env'
            env_path.touch()
            set_key(find_dotenv(), 'RUNIT_API_ENDPOINT', '')
            set_key(find_dotenv(), 'RUNIT_PROJECT_ID', '')

    @staticmethod
    def update_api_settings(args, settings):
        if args.api:
            settings['RUNIT_API_ENDPOINT'] = args.api
        else:
            for key, value in settings.items():
                new_value = input(f'{key} [{value}]: ').strip()
                if new_value:
                    settings[key] = new_value 
                else:
                    print(f'{key} cannot be empty')
                    print(f'Setting {key} to default [{value}]')

    @staticmethod
    def setup_runit(args):
        '''
        Setup Runit server side api

        @params args
        @return None
        '''
        settings = dotenv_values(find_dotenv())

        RunitServerSetup.create_default_env_file()
        RunitServerSetup.update_api_settings(args, settings)

        for key, value in settings.items():
            set_key(find_dotenv(), key, value)

# Example usage:
# setup = RunitServerSetup()
# setup.setup_runit(args)

class WebServer:
    def __init__(self, project):
        self.project = project

    def create_app(self):
        app = FastAPI()
        app.secret_key = os.getenv('SECRET_KEY')
        return app

    def add_routes(self, app):
        @app.api_route('/', methods=["GET", "POST"])
        @app.api_route('/{func}', methods=["GET", "POST"])
        @app.api_route('/{func}/', methods=["GET", "POST"])
        @app.api_route('/{func}/{output_format}', methods=["GET", "POST"])
        @app.api_route('/{func}/{output_format}/', methods=["GET", "POST"])
        async def serve(func: str = 'index', output_format: str = 'json', request: Request = None):
            response = self.handle_request(func, output_format, request)
            return self.process_response(output_format, response)

    def handle_request(self, func, output_format, request):
        response = {'status': True, 'data': {}}
        result = ''

        try:
            parameters = self.get_request_parameters(request)
            result = self.project.serve(func, parameters)
            self.check_404(result)
            response['data'] = self.parse_result(result)
        except json.decoder.JSONDecodeError:
            response['data'] = result
        except Exception:
            response['status'] = False
            response['message'] = self.project.notfound(output_format)

        return response

    async def get_request_parameters(self, request):
        parameters = request.query_params._dict
        if 'content-type' in request.headers.keys() and request.headers['content-type'] == "application/json":
            data = await request.json()
            parameters = {**parameters, **data}
        parameters.pop('output_format', None)
        return list(parameters.values()) if request else request

    def check_404(self, result):
        if result.startswith('404'):
            raise RuntimeError('Not Found')

    def parse_result(self, result):
        return json.loads(result.replace("'", '"'))

    def process_response(self, output_format, response):
        if output_format == 'html':
            return HTMLResponse(response['data'])
        else:
            return response

    def start(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        app = self.create_app()
        self.add_routes(app)

        try:
            uvicorn.run(app, host=host, port=port)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

# Example usage:
# web_server = WebServer(project_instance)
# web_server.start()

# import asyncio
# import websockets

# async def websocket_client():
#     uri = "ws://localhost:8765"  # replace with your server URI
#     async with websockets.connect(uri) as websocket:
#         await websocket.send("Hello, Server!")
#         response = await websocket.recv()
#         print(f"Received message from server: {response}")

# # To run the client program
# asyncio.get_event_loop().run_until_complete(websocket_client())
