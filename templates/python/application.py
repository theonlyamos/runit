#from packages import request

def index():
    return 'Hello World'

def counter():
    return [i for i in range(0, 9)]

def printout(string):
    return string

def time():
    from datetime import datetime
    return (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")