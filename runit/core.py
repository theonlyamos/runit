import asyncio
import os
import signal
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import sys
from pathlib import Path
from dotenv import find_dotenv, dotenv_values, set_key

from .constants import (
    RUNIT_HOMEDIR, SERVER_HOST, SERVER_PORT, VERSION
)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger('runit.server')


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
        try:
            if not find_dotenv(str(Path(RUNIT_HOMEDIR, '.env'))):
                env_path = Path(RUNIT_HOMEDIR) / '.env'
                env_path.touch()
                set_key(find_dotenv(), 'RUNIT_API_ENDPOINT', '')
            
            settings = dotenv_values(find_dotenv())

            RunitServerSetup.create_default_env_file()
            RunitServerSetup.update_api_settings(args, settings)

            for key, value in settings.items():
                set_key(find_dotenv(), key, str(value))
        except Exception as e:
            print(f"Error during setup: {e}")


import json


class WebServer:
    """Production-ready web server with health checks and graceful shutdown."""
    
    _shutdown_event: asyncio.Event = None

    def __init__(self, project):
        self.project = project
        self._startup_time = None
        self._request_count = 0

    def create_app(self):
        """Create FastAPI app with lifespan management."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.on_startup()
            yield
            await self.on_shutdown()
        
        app = FastAPI(
            title="Runit Server",
            description="Serverless function execution server",
            version=VERSION,
            lifespan=lifespan
        )
        return app

    async def on_startup(self):
        """Initialize server on startup."""
        self._startup_time = asyncio.get_event_loop().time()
        self._shutdown_event = asyncio.Event()
        logger.info("Runit server starting up...")
        
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.graceful_shutdown()))
            except NotImplementedError:
                pass

    async def on_shutdown(self):
        """Cleanup on shutdown."""
        logger.info("Runit server shutting down...")

    async def graceful_shutdown(self):
        """Handle graceful shutdown with signal."""
        logger.info("Received shutdown signal, initiating graceful shutdown...")
        self._shutdown_event.set()
        
        await asyncio.sleep(0.5)
        
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()

    def add_routes(self, app):
        """Add all routes including health check endpoints."""
        
        @app.get('/health')
        @app.get('/healthz')
        async def health_check():
            """Health check endpoint for load balancers and monitoring."""
            return JSONResponse({
                "status": "healthy",
                "uptime": asyncio.get_event_loop().time() - self._startup_time if self._startup_time else 0,
                "requests_served": self._request_count
            })

        @app.get('/ready')
        @app.get('/readyz')
        async def readiness_check():
            """Readiness check endpoint for Kubernetes."""
            return JSONResponse({
                "status": "ready",
                "project": self.project.name if hasattr(self.project, 'name') else "unknown"
            })

        @app.get('/metrics')
        async def metrics():
            """Basic metrics endpoint."""
            return JSONResponse({
                "uptime_seconds": asyncio.get_event_loop().time() - self._startup_time if self._startup_time else 0,
                "total_requests": self._request_count,
                "project": self.project.name if hasattr(self.project, 'name') else "unknown"
            })

        @app.api_route('/', methods=["GET", "POST"])
        @app.api_route('/{func}', methods=["GET", "POST"])
        @app.api_route('/{func}/', methods=["GET", "POST"])
        @app.api_route('/{func}/{output_format}', methods=["GET", "POST"])
        @app.api_route('/{func}/{output_format}/', methods=["GET", "POST"])
        
        async def serve(func: str = 'index', output_format: str = 'json', request: Request = None):
            self._request_count += 1
            parameters = await self.get_request_parameters(request)
            response = self.handle_request(func, output_format, parameters)
            return self.process_response(output_format, response)

    def handle_request(self, func, output_format, parameters):
        response = ''
        result = ''
        try:
            result = self.project.serve(func, parameters)
            self.check_404(result)
            response = self.parse_result(result)
        except json.decoder.JSONDecodeError:
            response = result
        except Exception:
            response = self.project.notfound(output_format)
        finally:
            return response

    async def get_request_parameters(self, request: Request) -> list:
        """Extract request parameters safely."""
        data = {}

        try:
            if request.method.lower() == 'post':
                if hasattr(request, '_form') and request._form is not None:
                    data = dict(request._form)
                
                content_type = request.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        data = await request.json()
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = dict(request.query_params)

            data.pop('output_format', None)
            
            return list(data.values()) if isinstance(data, dict) else []
        except Exception:
            return []

    def check_404(self, result):
        if '404' in result:
            raise RuntimeError('Not Found')

    def parse_result(self, result):
        return json.loads(result.replace("'", '"'))

    def process_response(self, output_format, response):
        if output_format == 'html':
            return HTMLResponse(response['data'])
        else:
            return response

    def start(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        """Start the server with production-ready configuration."""
        app = self.create_app()
        self.add_routes(app)

        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=30,
            limit_concurrency=100,
            limit_max_requests=1000
        )
        
        server = uvicorn.Server(config)
        
        try:
            asyncio.run(server.serve())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)
