from typing import List, Dict
from datetime import datetime
import uuid

from bson.objectid import ObjectId

from common.database import Database
#from models import Function
#from models import User

class Project():
    def __init__(self, user_id, name, version="0.0.1", description="", homepage="",
    language="", framework="", runtime="", start_file="", author={}, created_at=None, updated_at=None, _id=None):
        self.name = name
        self.user_id = user_id
        self.version = version
        self.description = description
        self.homepage = homepage
        self.language = language
        self.runtime = runtime
        self.framework = framework,
        self.start_file = start_file
        self.author = author
        self.created_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not created_at else created_at
        self.updated_at = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S") \
            if not updated_at else updated_at
        self.id = str(uuid.uuid4()) if not _id else _id

    def save(self):
        '''
        Instance Method for saving Project instance to database

        @params None
        @return None
        '''

        data = {
            "name": self.name,
            "user_id": ObjectId(self.user_id),
            "version": self.version,
            "description": self.description,
            "homepage": self.homepage,
            "language": self.language,
            "runtime": self.runtime,
            "framework": self.framework,
            "start_file": self.start_file,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        return Database.db.projects.insert_one(data)
    
    def update(self, update: dict = {}):
        '''
        Instance Method for updating Project instance to database

        @params None
        @return None
        '''
        update['updated_at'] = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
        
        return Database.db.projects.update_one({'_id': ObjectId(self.id)}, {'$set': update}, upsert=True)

    def user(self):#-> User:
        '''
        Instance Method for retrieving User of Project instance
        
        @params None
        @return User Instance
        '''

        #return User.get(self.user_id)
        return Database.db.users.find_one({'_id': ObjectId(self.user_id)})
    
    def functions(self)-> List:#[Function]:
        '''
        Instance Method for retrieving Functions of Project Instance

        @params None
        @return List of Function Instances
        '''

        #return Function.get(self.id)
        return Database.db.functions.find({'project_id': ObjectId(self.id)})
    
    def count_functions(self)-> int:
        '''
        Instance Method for counting function in Project

        @params None
        @return Count of functions
        '''

        return Database.db.functions.count_documents({'project_id': ObjectId(self.id)})
    
    def json(self)-> Dict:
        '''
        Instance Method for converting instance to Dict

        @paramas None
        @return Dict() format of Project instance
        '''
        return {
            "_id": str(self.id),
            "name": self.name,
            "user_id": str(self.user_id),
            "version": self.version,
            "description": self.description,
            "homepage": self.homepage,
            "language": self.language,
            "runtime": self.runtime,
            "framework": self.framework,
            "start_file": self.start_file,
            "author": self.author,
            "functions": self.count_functions(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def get_by_user(cls, user_id: str)-> List:
        '''
        Class Method for retrieving projects by a user

        @param user_id:str _id of the user
        @return List of Project instances
        '''
        projects = Database.db.projects.find({'user_id': ObjectId(user_id)})
        return [cls(**elem) for elem in projects]

    @classmethod
    def get(cls,  _id = None):
        '''
        Class Method for retrieving project(s) by _id 
        or all if _id is None

        @param _id ID of the project in databse
        @return Project instance
        '''

        if _id is None:
            return [cls(**elem) for elem in Database.db.projects.find({})]
            
        project = Database.db.projects.find_one({"_id": ObjectId(_id)})
        return cls(**project) if project else None

