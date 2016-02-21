import sqlite3
import logging
from functools import wraps

from flask import Blueprint, Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response

from twirps import app, data_collection


LOGGER = logging.getLogger(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     pass

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


################################################################################
#                                ADMIN BACKEND                                 #
################################################################################

def read_log():
    for line in  open('./tmp/twirps.log', "r"):
        yield line

@app.route('/admin_login/', methods=['GET', 'POST'])
@requires_auth
def view_backend():
    LOGGER.info("Loading backend")

    return render_template('backend.html', rows=read_log())

@app.route('/admin_login/start_stream', methods=['GET', 'POST'])
@requires_auth
def add_twirp():
    LOGGER.info("Received start stream message")
    
    data_collection.start_stream()
    return render_template('backend.html', rows=read_log())

@app.route('/admin_login/stop_stream', methods=['GET','POST'])
@requires_auth
def stop_stream():
    LOGGER.info("Received stop stream message")
    
    data_collection.stop_stream()
    return render_template('backend.html', rows=read_log())


################################################################################
#                                  SHUTDOWN                                    #
################################################################################


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/admin_login/shutdown', methods=['GET','POST'])
def shutdown():
    shutdown_server()
    LOGGER.info( 'Server shutting down...')