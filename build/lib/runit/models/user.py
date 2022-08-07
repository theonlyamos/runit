from datetime import datetime
from typing import Dict, List
import uuid

from bson.objectid import ObjectId

from common.database import Database
from common.utils import Utils
#from models import Project
#from models import Function


class User():
    '''A model class for user'''

    def __init__(self, email, name, password, created_at=None, updated_at=None, _id=None):
        self.email = email
        self.name = name
        self.password = password
        self.created_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not created_at else created_at
        self.updated_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not updated_at else updated_at
        self.id = uuid.uuid4() if not _id else str(_id)

    def save(self):
        '''
        Instance Method for saving User instance to database

        @params None
        @return None
        '''

        data = {
            "name": self.name,
            "email": self.email,
            "password": Utils.hash_password(self.password),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        return Database.db.users.insert_one(data)
    
    def update(self, update: Dict):
        '''
        Instance Method for updating user in database

        @param update Content to be update in dictionary format
        @return None
        '''

        Database.db.users.update_one({'_id': ObjectId(self.id)}, update)
    
    def reset_password(self, new_password: str):
        '''
        Instance Method for resetting user password

        @param new_password User's new password
        @return None
        '''

        Database.db.users.update_one({'_id': ObjectId(self.id)}, {'password': new_password})
        self.password = new_password
    
    def projects(self):#-> List[Project]:
        '''
        Instance Method for retrieving Projects of User Instance

        @params None
        @return List of Project Instances
        '''

        #return Project.get_by_user(self.id)
        return Database.db.projects.find({'user_id': ObjectId(self.id)})
    
    def functions(self):#-> List[Function]:
        '''
        Instance Method for retrieving Functions of User Instance

        @params None
        @return List of Function Instances
        '''

        #return Function.get_by_user(self.id)
        return Database.db.functions.find({'user_id': ObjectId(self.id)})

    def count_functions(self)-> int:
        '''
        Instance Method for counting User functions

        @params None
        @return int Count of functions
        '''

        return Database.db.functions.count_documents({'user_id': ObjectId(self.id)})

    def count_projects(self)-> int:
        '''
        Instance Method for counting User Projects

        @params None
        @return int Count of Projects
        '''

        return Database.db.projects.count_documents({'user_id': ObjectId(self.id)})
    
    def json(self)-> Dict:
        '''
        Instance Method for converting User Instance to Dict

        @paramas None
        @return dict() format of Function instance
        '''

        return {
            "_id": str(self.id),
            "name": self.name,
            "email": self.email,
            "projects": self.count_projects(),
            "functions": self.count_functions(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def get_by_email(cls, email: str):
        '''
        Class Method for retrieving user by email address

        @param email email address of the user 
        @return User instance
        '''
        user = Database.db.users.find_one({"email": email})
        return cls(**user) if user else None

    @classmethod
    def get(cls, _id = None):
        '''
        Class Method for retrieving function(s) by _id 
        or all if _id is None

        @param _id ID of the function in database
        @return Function instance(s)
        '''

        if _id is None:
            return [cls(**elem) for elem in Database.db.users.find({})]

        user = Database.db.users.find_one({"_id": ObjectId(_id)})
        return cls(**user) if user else None
