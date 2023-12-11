import os
import sys
import shelve
from getpass import getpass

import requests
from dotenv import load_dotenv

# from ..constants import API_VERSION

load_dotenv()
BASE_API = f"{os.getenv('RUNIT_API_ENDPOINT')}/"
PROJECTS_API = BASE_API+'projects/'
RUNIT_HOMEDIR = os.path.dirname(os.path.realpath(__file__))
BASE_HEADERS = {}

def load_token(access_token = None):
    curdir = os.curdir
    os.chdir(RUNIT_HOMEDIR)
    with shelve.open('account') as account:
        if access_token is None and 'access_token' in account.keys():
            return account['access_token']
        if access_token:
            account['access_token'] = access_token
        else:
            account['access_token'] = ''
    os.chdir(curdir)
    return None

class Account():
    '''Class for managing user account'''

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
    def login(args):
        '''
        Accoun Login Method

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

            request = requests.post(url, json=data)

            result = request.json()

            if 'access_token' in result.keys():
                token = load_token(result['access_token'])
                print('[Success] Logged in successfully')
            elif 'detail' in result.keys():
                print('[Error]', result['detail'])
            else:
                print('[Error]', result['message'])
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
            token = load_token('')
            print('[Success] Logged out successfully!')
        except Exception as e:
            print(str(e))
        
    @staticmethod
    def isauthenticated(args):
        '''
        Check if current user is authenticated
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + 'account/'

            request = requests.get(url, headers=BASE_HEADERS)
            result = request.json()
            if 'detail' in result.keys():
                raise Exception(result['detail'])

        except Exception as e:
            print(str(e))
            sys.exit(1)
    
    @staticmethod
    def user()-> dict:
        '''
        Retrieve account details
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + 'account/'

            request = requests.get(url, headers=BASE_HEADERS)
            result = request.json()
            if 'detail' in result.keys():
                raise Exception(result['detail'])
            return result

        except Exception as e:
            #print(str(e))
            return {}
  
    @staticmethod
    def info(args):
        '''
        Retrieve account details
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + 'account/'
            
            request = requests.get(url, headers=BASE_HEADERS)
            result = request.json()

            if 'message' in result.keys():
                raise Exception('[Error] '+result['message'])
            if 'detail' in result.keys():
                raise Exception('[Error] '+result['detail'])
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
    def projects(args):
        '''
        Retrieve Project Info
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()
            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + 'projects/'

            if args.id:
                url += f'{args.id}'

            request = requests.get(url, headers=BASE_HEADERS)
            results = request.json()
            
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
                    print("="*20)

        except Exception as e:
            print(str(e))
    
    @staticmethod
    def publish_project(files, data: dict):
        '''
        Retrieve account details
        
        @param files Zipfile of project
        @param data Project Config
        @return requests response
        '''
        
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"
            url = PROJECTS_API + 'publish'

            req = requests.post(url, data=data, 
                        files=files, headers=BASE_HEADERS)
            result = req.json()
            
            return result

        except Exception as e:
            print(str(e))
            sys.exit(1)
    
    @staticmethod
    def clone_project(project: str):
        '''
        Clone project to current directory
        
        @param files Zipfile of project
        @param data Project Config
        @return requests response
        '''
        
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"
            
            url = BASE_API + f'projects/clone/{project}'

            response = requests.get(url, headers=BASE_HEADERS)

            if (response.headers['Content-Type'] == 'application/json'):
                result = response.json()

                if 'message' in result.keys() and len(result['message']):
                    raise Exception(f"[Error] {result['message']}")
            return response.content

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
    def update_project(args):
        '''
        Static Method for updating Project
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()
            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + f'projects/{args.id}'

            data = {}
            raw = args.data
            for r in raw:
                key, value = r.split('=')
                data[key] = value
            
            request = requests.post(url, json=data, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
    
    @staticmethod
    def delete_project(args):
        '''
        Static Method for deleting Project
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()
            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + f'projects/{args.id}'

            request = requests.delete(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
    
    @staticmethod
    def functions(args):
        '''
        Retrieve Functions
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()
            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_API + 'functions'

            if args.project:
                url += f'/{args.project}'
            
            if args.id:
                url += f'/{args.id}'

            request = requests.get(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
