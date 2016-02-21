from __future__ import unicode_literals
import os
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
    ''' Use to render & parse if necc'''
    for line in  open('./tmp/twirps.log', "r"):
        yield line.decode('utf-8').strip()

@app.route('/admin/', methods=['GET', 'POST'])
@requires_auth
def view_backend():
    if request.method=='POST':
        if request.form["submit"]== "start_stream":
            LOGGER.info("Received start stream message")
            data_collection.start_stream()
        elif request.form["submit"]== "stop_stream":
            LOGGER.info("Received stop stream message")
            data_collection.stop_stream()
        elif request.form["submit"]== "shutdown":
            LOGGER.info("Received stop stream message")
            shutdown_server()
        elif request.form["submit"]=="log_resolution":
            LOGGER.info("Received change log resolution message")
            new_res = request.form["resolution"]
            data_collection.change_stream_resolution(int(new_res))

    res = data_collection.get_stream_resolution()
    LOGGER.debug("Loading backend")
    return render_template('backend.html', stream_res=res, rows=read_log())

@app.route('/admin/db_edit', methods=['GET', 'POST'])
@requires_auth
def db_edit():
    if request.method=='POST':
        if request.form["submit"]== "start_stream":
            LOGGER.info("Received start stream message")
            data_collection.start_stream()
        elif request.form["submit"]== "stop_stream":
            LOGGER.info("Received stop stream message")
            data_collection.stop_stream()
        elif request.form["submit"]== "shutdown":
            LOGGER.info("Received stop stream message")
            shutdown_server()
        elif request.form["submit"]=='log_resolution':
            pass

    LOGGER.debug("Loading backend")
    return render_template('interact_database.html', response_data=[{1:2,3:4}])


################################################################################
#                                  SHUTDOWN                                    #
################################################################################


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/admin/shutdown', methods=['GET','POST'])
def shutdown():
    shutdown_server()
    LOGGER.info( 'Server shutting down...')