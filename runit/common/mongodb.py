from flask_pymongo import PyMongo
from flask import Flask

import os
from dotenv import load_dotenv

load_dotenv()


class MongoDB(object):
    db = None

    @staticmethod
    def initialize(app, host, port, database, user=None, password=None):
        client = PyMongo()
        app.config['MONGO_URI'] = f'mongodb://{host}:{port}/{database}'
        client.init_app(app)
        MongoDB.db = client.db
        #MongoDB.db = client['runit']

    @staticmethod
    def insert(collection, data):
        MongoDB.db[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return MongoDB.db[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return MongoDB.db[collection].find_one(query)

    @staticmethod
    def remove(collection, query):
        MongoDB.db[collection].remove(query)

    @staticmethod
    def update(collection, query, data):
        MongoDB.db[collection].update_one(query, data, upsert=True)

