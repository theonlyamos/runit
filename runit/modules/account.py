import os
import sys
import time
import logging
from getpass import getpass
from typing import Optional, Dict, Any
from functools import wraps

import keyring  # type: ignore
import keyring.errors  # type: ignore
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('runit.account')

BASE_API = f"{os.getenv('RUNIT_API_ENDPOINT')}/"
PROJECTS_API = BASE_API + 'projects/'
RUNIT_HOMEDIR = os.path.dirname(os.path.realpath(__file__))
BASE_HEADERS = {'Content-Type': 'application/json'}
KEYRING_SERVICE = "runit-cli"

MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
REQUEST_TIMEOUT = 30


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
    def register(args):
        '''
        Static Method for account registration

        @param args Input from argparse
        @return None
        '''
        try:
            pass
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
            url = BASE_API + 'login'

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
            url = BASE_API + 'account/'
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
            url = BASE_API + 'account/'
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
            url = BASE_API + 'account/'
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
            url = BASE_API + 'projects/'

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
            url = PROJECTS_API + 'publish'
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
            result = response.json()
            
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
            url = BASE_API + f'projects/clone/{project}'
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
            url = BASE_API + f'projects/{args.id}'

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
            url = BASE_API + f'projects/{args.id}'

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
            url = BASE_API + 'functions'

            if args.project:
                url += f'/{args.project}'
            
            if args.id:
                url += f'/{args.id}'

            session = get_http_session()
            response = session.get(url, headers=Account._get_headers(), timeout=REQUEST_TIMEOUT)
            print(response.json())

        except Exception as e:
            print(str(e))
