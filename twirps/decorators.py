from functools import wraps
from threading import Thread 

from flask import request



def check_auth(username, password):
    return username == "condnsdmatters" and password == 'password'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def async(f):
    @wraps(f)
    def decorated(*args, **kwargs):
       thr = Thread(target=f, args=args, kwargs=kwargs)
       thr.setDaemon(True)
       thr.start()
       return thr
    return decorated
    