from flask_pymongo import PyMongo
from flask import Flask
from runit import app
import os


class Database(object):
    #URI = os.getenv('FAFMONGO')
    db = None

    @staticmethod
    def initialize():
        client = PyMongo()
        app.config['MONGO_URI'] = os.getenv('FAFMONGO', 'mongodb://localhost:27017')+'/runit'
        client.init_app(app)
        Database.db = client.db
        #Database.DATABASE = client['runit']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].remove(query)

    @staticmethod
    def update(collection, query, data):
        Database.DATABASE[collection].update_one(query, data, upsert=True)

