#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2022-08-06 17:37:00
# @Author  : Amos Amissah (theonlyamos@gmail.com)
# @Link    : link
# @Version : 1.0.0

class Database:
    db = None

    @staticmethod
    def initialize(dbsettings: dict, app=None):
        if dbsettings['dbms'] == 'mongodb':
            from .mongodb import MongoDB
            MongoDB.initialize(app, dbsettings['dbhost'], 
                dbsettings['dbport'],
                dbsettings['dbname'])
            Database.db = MongoDB.db
        elif dbsettings['dbms'] == 'mysql':
            from .mysql import MysqlDB
            MysqlDB.initialize(dbsettings['dbhost'], 
                dbsettings['dbport'],
                dbsettings['dbname'],
                dbsettings['dbusername'],
                dbsettings['dbpassword'])
            Database = MysqlDB
