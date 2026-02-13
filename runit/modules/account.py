import os
import sys
import time
import logging
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from getpass import getpass
from typing import Optional, Dict, Any
from functools import wraps

import keyring  # type: ignore
import keyring.errors  # type: ignore
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse, urlencode, parse_qs
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('runit.account')

RUNIT_HOMEDIR = os.path.dirname(os.path.realpath(__file__))
BASE_HEADERS = {'Content-Type': 'application/json'}
KEYRING_SERVICE = "runit-cli"

MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
REQUEST_TIMEOUT = 30


def get_base_api() -> str:
    """Get validated API base URL from environment."""
    endpoint = os.getenv('RUNIT_API_ENDPOINT')
    if not endpoint:
        raise RuntimeError(
            "RUNIT_API_ENDPOINT is not set. Run `runit setup --api http://<host>/api/v1` first."
        )

    endpoint = endpoint.strip().rstrip('/')
    parsed = urlparse(endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(
            f"Invalid RUNIT_API_ENDPOINT: '{endpoint}'. Expected full URL like http://localhost:9000/api/v1"
        )

    return endpoint + '/'


def create_session_with_retry() -> requests.Session:
    """Create a requests session with connection pooling and retry logic."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        raise_on_status=False
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


_http_session: Optional[requests.Session] = None


def get_http_session() -> requests.Session:
    """Get or create the shared HTTP session."""
    global _http_session
    if _http_session is None:
        _http_session = create_session_with_retry()
    return _http_session


def with_retry(max_retries: int = MAX_RETRIES, backoff_factor: float = RETRY_BACKOFF_FACTOR):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.HTTPError) as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}), "
                                      f"retrying in {wait_time:.1f}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Request failed after {max_retries + 1} attempts: {e}")
                        raise
            raise RuntimeError("Unexpected state in retry logic")
        return wrapper
    return decorator


def load_token(access_token=None):
    """
    Securely store and retrieve access tokens using system keyring.
    
    Args:
        access_token: If provided, stores the token. If None, retrieves it.
                     If empty string, deletes the token.
    
    Returns:
        The stored token when retrieving, None otherwise.
    
    Raises:
        RuntimeError: If keyring backend is unavailable.
    """
    try:
        if access_token is None:
            return keyring.get_password(KEYRING_SERVICE, "access_token")
        elif access_token:
            keyring.set_password(KEYRING_SERVICE, "access_token", access_token)
            return None
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, "access_token")
            except keyring.errors.PasswordDeleteError:
                pass
            return None
    except keyring.errors.KeyringError as e:
        raise RuntimeError(
            f"Keyring backend unavailable: {e}. "
            "Please install a keyring backend for your OS."
        ) from e


class Account():
    '''Class for managing user account'''

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Get headers with authorization token."""
        headers = BASE_HEADERS.copy()
        token = load_token()
        if token:
            headers['Authorization'] = f"Bearer {token}"
        return headers

    @staticmethod
    def _get_base_web() -> str:
        """Derive base web URL from configured API URL."""
        api_url = get_base_api().rstrip("/")
        parsed = urlparse(api_url)
        path = parsed.path.rstrip("/")

        if path.endswith("/api/v1"):
            path = path[: -len("/api/v1")]
        elif "/api/" in path:
            path = path.split("/api/", maxsplit=1)[0]

        web_url = parsed._replace(path=path or "", params="", query="", fragment="").geturl().rstrip("/")
        if not web_url:
            raise RuntimeError("Unable to derive web URL from RUNIT_API_ENDPOINT")
        return web_url

    @staticmethod
    def auth(args):
        """
        Authenticate in browser and receive token via local callback server.
        """
        try:
            direct_token = getattr(args, 'token', None)
            if direct_token:
                load_token(str(direct_token).strip())
                print('[Success] Token stored successfully')
                return

            web_base = Account._get_base_web()
            callback_state: Dict[str, Optional[str]] = {"access_token": None, "error": None}
            callback_complete = threading.Event()

            class CallbackHandler(BaseHTTPRequestHandler):
                def log_message(self, format, *args):
                    return

                def do_GET(self):
                    parsed_path = urlparse(self.path)
                    if parsed_path.path != '/callback':
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Not Found')
                        return

                    params = parse_qs(parsed_path.query)
                    access_token = params.get('access_token', [None])[0]

                    if access_token:
                        callback_state["access_token"] = access_token
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(
                            b"<html><body><h3>Authentication complete.</h3>"
                            b"<p>You can close this window and return to your terminal.</p></body></html>"
                        )
                    else:
                        callback_state["error"] = "Missing access token in callback response"
                        self.send_response(400)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(
                            b"<html><body><h3>Authentication failed.</h3>"
                            b"<p>Access token was not received.</p></body></html>"
                        )
                    callback_complete.set()

            callback_server = ThreadingHTTPServer(('127.0.0.1', 0), CallbackHandler)
            callback_port = callback_server.server_address[1]
            callback_thread = threading.Thread(target=callback_server.serve_forever, daemon=True)
            callback_thread.start()

            redirect_uri = f"http://127.0.0.1:{callback_port}/callback"
            auth_url = f"{web_base}/auth/cli?{urlencode({'redirect_uri': redirect_uri})}"

            print("[Info] Waiting for browser authentication...")
            print(f"[Info] If browser does not open, visit: {auth_url}")

            if not getattr(args, 'no_open', False):
                webbrowser.open(auth_url)

            completed = callback_complete.wait(timeout=300)
            callback_server.shutdown()
            callback_server.server_close()
            callback_thread.join(timeout=2)

            if not completed:
                print('[Error] Authentication timed out after 5 minutes')
                return

            if callback_state["access_token"]:
                load_token(callback_state["access_token"])
                print('[Success] Logged in successfully')
                return

            print(f"[Error] {callback_state['error'] or 'Authentication failed'}")
        except Exception as e:
            print(str(e))

    @staticmethod
    def register(args):
        '''
        Static Method for account registration

        @param args Input from argparse
        @return None
        '''
        try:
            name = args.name
            email = args.email
            password = args.password
            cpassword = getattr(args, 'cpassword', None)

            while not name:
                name = str(input('Full Name: '))
            while not email:
                email = str(input('Email Address: '))
            while not password:
                password = getpass()
            while not cpassword:
                cpassword = getpass('Confirm Password: ')

            if password != cpassword:
                print('[Error] Passwords do not match')
                return

            data = {
                "name": name,
                "email": email,
                "password": password,
                "cpassword": cpassword
            }
            url = get_base_api() + 'register'

            session = get_http_session()
            response = session.post(url, json=data, timeout=REQUEST_TIMEOUT)
            result = response.json()

            if 'access_token' in result.keys():
                load_token(result['access_token'])
                print('[Success] Registration successful')
            elif 'detail' in result.keys():
                print('[Error]', result['detail'])
            else:
                print('[Error]', result.get('message', 'Unknown error'))
        except Exception as e:
            print(str(e))

    @staticmethod
    @with_retry()
    def login(args):
        '''
        Account Login Method

        @args Input from argparse containing email and password
        @return None
        '''
        try:
            email = args.email
            password = args.password

            while not email:
                email = str(input('Email Address: '))
            while not password:
                password = getpass()

            data = {"email": email, "password": password}
            url = get_base_api() + 'login'

            session = get_http_session()
            response = session.post(url, json=data, timeout=REQUEST_TIMEOUT)
            result = response.json()

            if 'access_token' in result.keys():
                load_token(result['access_token'])
                print('[Success] Logged in successfully')
            elif 'detail' in result.keys():
                print('[Error]', result['detail'])
            else:
                print('[Error]', result.get('message', 'Unknown error'))
        except Exception as e:
            print(str(e))

    @staticmethod
    def logout(args):
        '''
        Logout of Current Account

        @param args Input from argparse
        @return None
        '''
        try:
            load_token('')
            print('[Success] Logged out successfully!')
        except Exception as e:
            print(str(e))

    @staticmethod
    @with_retry()
    def isauthenticated():
        '''
        Check if current user is authenticated
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + 'account/'
            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            result = response.json()
            
            if 'detail' in result.keys():
                raise Exception(result['detail'])
            elif not len(result.keys()):
                raise Exception('[Error] User is not authenticated')

        except Exception as e:
            print(str(e))
            sys.exit(1)

    @staticmethod
    @with_retry()
    def user() -> dict:
        '''
        Retrieve account details
        
        @param args Input from argparse
        @return dict Account information
        '''
        try:
            url = get_base_api() + 'account/'
            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            result = response.json()
            
            if 'detail' in result.keys():
                raise Exception(result['detail'])
            return result

        except Exception as e:
            return {}

    @staticmethod
    @with_retry()
    def info(args):
        '''
        Retrieve account details
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + 'account/'
            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            result = response.json()

            if 'message' in result.keys():
                raise Exception('[Error] ' + result['message'])
            if 'detail' in result.keys():
                raise Exception('[Error] ' + result['detail'])
            print()
            for key, value in result.items():
                if len(key) < 7:
                    print(f"{key}:\t\t{value}")
                else:
                    print(f"{key}:\t{value}")

        except Exception as e:
            print(str(e))
            sys.exit(1)

    @staticmethod
    @with_retry()
    def projects(args):
        '''
        Retrieve Project Info
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + 'projects/'

            if args.id:
                url += f'{args.id}'

            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            results = response.json()

            if isinstance(results, dict):
                print()
                for key, value in results.items():
                    if len(key) < 7:
                        print(f"{key}:\t\t{value}")
                    else:
                        print(f"{key}:\t{value}")
            else:
                for project in results:
                    print()
                    print(f"ID:\t\t{project['id']}")
                    print(f"Name:\t\t{project['name']}")
                    print(f"Description:\t{project['description']}")
                    print("=" * 20)

        except Exception as e:
            print(str(e))

    @staticmethod
    @with_retry()
    def publish_project(files, data: dict):
        '''
        Publish project to server
        
        @param files Zipfile of project
        @param data Project Config
        @return requests response
        '''
        try:
            url = get_base_api() + 'projects/publish'
            session = get_http_session()
            
            headers = Account._get_headers()
            headers.pop('Content-Type', None)
            
            response = session.post(
                url, 
                data=data, 
                files=files, 
                headers=headers,
                timeout=REQUEST_TIMEOUT * 2
            )
            try:
                result = response.json()
            except json.JSONDecodeError:
                message = response.text.strip() if response.text else "Empty response from server"
                return {
                    "status": "error",
                    "message": f"Publish request failed with HTTP {response.status_code}: {message[:300]}"
                }
            
            return result

        except Exception as e:
            print(str(e))
            sys.exit(1)

    @staticmethod
    @with_retry()
    def clone_project(project: str):
        '''
        Clone project to current directory
        
        @param project Project ID or name
        @return requests response
        '''
        try:
            url = get_base_api() + f'projects/clone/{project}'
            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT * 2)

            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                result = response.json()

                if 'message' in result.keys() and len(result['message']):
                    raise Exception(f"[Error] {result['message']}")
                
            return response

        except Exception as e:
            print(str(e))
            sys.exit(1)

    @staticmethod
    def create_project(args):
        '''
        Static Method for creating new Project
        
        @param args Input from argparse
        @return None
        '''
        pass

    @staticmethod
    @with_retry()
    def update_project(args):
        '''
        Static Method for updating Project
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + f'projects/{args.id}'

            data = {}
            raw = args.data
            for r in raw:
                try:
                    key, value = r.split('=', 1)
                    data[key.strip()] = value.strip()
                except ValueError:
                    print(f"[Error] Invalid data format: '{r}'. Expected 'key=value'")
                    continue

            session = get_http_session()
            response = session.post(url, json=data, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            print(response.json())

        except Exception as e:
            print(str(e))

    @staticmethod
    @with_retry()
    def delete_project(args):
        '''
        Static Method for deleting Project
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + f'projects/{args.id}'

            session = get_http_session()
            response = session.delete(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            print(response.json())

        except Exception as e:
            print(str(e))

    @staticmethod
    @with_retry()
    def functions(args):
        '''
        Retrieve Functions
        
        @param args Input from argparse
        @return None
        '''
        try:
            url = get_base_api() + 'functions'

            if args.project:
                url += f'/{args.project}'
            
            if args.id:
                url += f'/{args.id}'

            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            print(response.json())

        except Exception as e:
            print(str(e))
