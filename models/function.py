from datetime import datetime
from typing import Dict
import uuid

from bson.objectid import ObjectId

from common.database import Database
#from models import Project
#from models import User

EXTENSIONS = {'python': '.py', 'python3': '.py', 'php': '.php', 'javascript': '.js'}

class Function():
    def __init__(self, name, user_id, language, project_id=None, filename=None, description=None, created_at=None, updated_at=None, _id=None):
        self.name = name
        self.filename = filename
        self.user_id = user_id
        self.project_id = project_id
        self.language = language
        self.description = description
        self.created_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not created_at else created_at
        self.updated_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not updated_at else updated_at
        self.id = uuid.uuid4() if not _id else _id

    def save(self):
        '''
        Instance Method for saving Function instance to database

        @params None
        @return None
        '''
        data = {
            "name": self.name,
            "filename": self.filename,
            "user_id": ObjectId(self.user_id),
            "language": self.language,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        if self.project_id:
            data['project_id'] = ObjectId(self.project_id) if self.project_id else self.project_id

        Database.db.functions.insert_one(data)
    
    def project(self):#-> Project:
        '''
        Instance Method for retrieving Project Instance of Function Instance

        @params None
        @return Project Instance
        '''

        #return Project.get(self.project_id)
        return Database.db.projects.find_one({'_id': ObjectId(self.project_id)})

    def user(self):#-> User:
        '''
        Instance Method for retrieving User of Function instance
        
        @params None
        @return User instance
        '''

        #return User.get(self.user_id)
        return Database.db.users.find_one({'_id': ObjectId(self.user_id)})
    
    def json(self)-> Dict:
        '''
        Instance Method for converting instance to dict()

        @paramas None
        @return dict() format of Function instance
        '''
        return {
            "_id": str(self.id),
            "name": self.name,
            "filename": self.filename,
            "language": self.language[0],
            "description": self.description,
            "user": self.user(),
            "project": self.project() if self.project_id else {},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def get_by_user(cls, user_id: str):
        '''
        Class Method for retrieving functions by a user

        @param user_id:str _id of the user
        @return List of Function instances
        '''
        functions = Database.db.functions.find({'user_id': ObjectId(user_id)})
        return [cls(**elem).json() for elem in functions]

    @classmethod
    def get(cls, _id):
        '''
        Class Method for retrieving function by _id

        @param _id ID of the function in databse
        @return Function instance
        '''
        function = Database.db.functions.find_one({"_id": ObjectId(_id)})
        return cls(**function) if function else None

    @classmethod
    def get_all(cls):
        '''
        Class Method for retrieving all functions from database

        @params None
        @return List of Function instances
        '''
        return [cls(**elem).json() for elem in Database.db.find("functions", {})]
