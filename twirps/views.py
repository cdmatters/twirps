from __future__ import unicode_literals
import os
import sqlite3
import logging
import json
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
    if request.method=='GET':
        LOGGER.debug("Loading admin panel")

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
    return render_template('backend.html', stream_res=res, rows=read_log())

@app.route('/admin/db_edit', methods=['GET', 'POST'])
@requires_auth
def db_edit():


    results = []
    if request.method=='POST':
        if request.form["submit"] in  ["get_twirps", 'subscribe','unsubscribe']:
            u_ids_string = request.form["u_ids"].split(',')
            handles_string = request.form["handles"].split(',')
            names_string = request.form["names"].split(',')
            usernames_string = request.form["usernames"].split(',')

            u_ids = [ u for u in u_ids_string ] if u_ids_string != [u''] else []
            handles = handles_string if handles_string != [u''] else []
            names = names_string if names_string != [u''] else []
            usernames = usernames_string if usernames_string != [u''] else []

            is_empty_input = not (u_ids or handles or names or usernames)
            
            results =  data_collection.get_user_data_from_identifiers(
                                                u_ids, handles, names, usernames)


            if request.form["submit"]=="subscribe" and not is_empty_input:
                subscribers = set(data_collection.get_subscribers_from_twitter())
                for r in results:
                    if r["u_id"] not in subscribers:
                        success = data_collection.subscribe_Twirp(r["name"], r["handle"], r["u_id"])
                        if success:
                            LOGGER.info("Subscribed to user %s" %r['handle'])
                    else:
                        LOGGER.warning("Already subscribed to user %s" %r['handle'])
            elif request.form["submit"]=="unsubscribe" and not is_empty_input:
                subscribers = set(data_collection.get_subscribers_from_twitter())
                for r in results:
                    if r["u_id"] in subscribers:
                        success = data_collection.unsubscribe_Twirp(r["name"], r["handle"], r["u_id"])
                        if success:
                            LOGGER.info("Unsubscribed to user %s" %r['handle'])
                    else:
                        LOGGER.warning("Already not following user %s" %r['handle'])

            
        elif request.form["submit"]== "delete_twirp":
            u_id = request.form["u_ids"]
            handle = request.form["handles"]
            name = request.form["names"]
            username = request.form["usernames"]
            
            LOGGER.info("Attempting to delete %s %s %s %s:"% (name, username, handle, u_id))
            success = data_collection.delete_Twirp(name, username, handle, u_id)
            if success == 0:
                results = ['Nothing deleted']
            elif success == 1:
                results = ['Success']
            else:
                results = ["Error"]
            results.extend(data_collection.get_user_data_from_identifiers([], [handle], [name], []) )


        elif request.form["submit"]== "add_twirp":
            name = request.form["names"]
            handle = request.form["handles"]
            LOGGER.info("Adding %s->%s"%(name, handle))
            if name != '' and handle != '':
                data_collection.add_Twirp_to_Twirps(name, handle)
                results =  data_collection.get_user_data_from_identifiers([], [handle], [name], [])
            else:
                results=['Please add both name and handle']
        elif request.form["submit"]=='log_resolution':
            pass
    


    return render_template('interact_database.html', results=results)


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