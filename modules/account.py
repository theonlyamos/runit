import os
import shelve
import requests
from getpass import getpass

BASE_URL = os.getenv('RUNIT_SERVERNAME', 'localhost:9000')+'api/'
BASE_HEADERS = {
    'Content-Type': 'application/json'
}

def load_token(access_token: str|None = None):
    curdir = os.curdir
    os.chdir(os.getenv('RUNIT_HOMEDIR'))
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
    def register(ars):
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
            url = BASE_URL + 'login/'

            request = requests.post(url, json=data)

            result = request.json()

            if 'access_token' in result.keys():
                token = load_token(result['access_token'])
                print('[Success] Logged in successfully')
            elif 'msg' in result.keys():
                print('[Error]', result['msg'])
            else:
                print('[Error]', result['message'])
        except Exception as e:
            print(str(e))
    
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
    def info(args)-> dict:
        '''
        Retrieve account details
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()

            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_URL + 'account/'

            request = requests.get(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
    
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

            url = BASE_URL + 'projects/'

            if not args.id is None:
                url += f'{args.id}/'

            request = requests.get(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
    
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

            url = BASE_URL + f'projects/{args.id}/'

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

            url = BASE_URL + f'projects/{args.id}/'

            request = requests.delete(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
    
    @staticmethod
    def functions(args)-> dict:
        '''
        Retrieve Functions
        
        @param args Input from argparse
        @return None
        '''
        try:
            global BASE_HEADERS
            token = load_token()
            BASE_HEADERS['Authorization'] = f"Bearer {token}"

            url = BASE_URL + 'functions/'

            if not args.project is None:
                url += f'{args.project}/'
            
            if not args.id is None:
                url += f'{args.id}/'

            request = requests.get(url, headers=BASE_HEADERS)
            print(request.json())

        except Exception as e:
            print(str(e))
