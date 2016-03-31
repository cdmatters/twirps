from __future__ import unicode_literals
import os

import logging
import json
from functools import wraps

from flask import Blueprint, Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response, jsonify

from werkzeug.routing import BaseConverter

from twirps import app, data_collection, data_assimilation

from decorators import requires_auth

# Where should this go? 
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


LOGGER = logging.getLogger(__name__)

app.url_map.converters['regex'] = RegexConverter

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', endpoint='/string')

@app.route('/data/string', methods=['GET'])
def test_call():
    return jsonify(data_assimilation.return_full_map())

# placeholder note for API
@app.route('/data/mouthpiece/{userid}', methods=['GET', 'POST'])
def mouthpiece():
    return render_template('index.html')

# placeholder note for API
@app.route('/data/nodes/{userid}/{neighbours}/{tweets}/{retweet}', methods=['GET', 'POST'])
def neighbours():
    return render_template('index.html')

# placeholder note for API
@app.route('/data/committees/{userid}/{tweets}/{retweets}', methods=['GET', 'POST'])
def committees():
    return render_template('index.html')

@app.route('/data/party/<regex("[a-zA-Z0-9_]{4,35}"):party>', methods=['GET'])
def get_parties(party):
    party = party.replace('_', ' ')
    return jsonify(data_assimilation.return_party_nodes(party))

@app.route('/party/<regex("[a-zA-Z0-9_]{4,35}"):party>', methods=['GET'])
def redirect_get_parties(party):
    return render_template('index.html', endpoint='/party/'+ party)

################################################################################
#                                ADMIN BACKEND                                 #
################################################################################

def read_log():
    ''' Use to render & parse if necc'''
    for line in  open('twirps.log', "r"):
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
        elif request.form["submit"]=="bulk_twirps_collect":
            LOGGER.info("Received get bulk twirps message")
            data_collection.get_bulk_twirps_main_async()
        elif request.form["submit"]=="bulk_hist_tweets_collect":
            LOGGER.info("Received get bulk tweets message")
            max_tweets = int(request.form["bulk_hist_tweet_no"])
            tweet_buffer = int(request.form["bulk_tweet_buffer"])
            data_collection.get_bulk_tweets_main_async(max_tweets, tweet_buffer)
        elif request.form["submit"]=="bulk_new_tweets_collect":
            LOGGER.info("Received get bulk new tweets")
            max_tweets = int(request.form["bulk_new_tweet_no"])
            data_collection.get_bulk_recent_tweet_async(max_tweets)


    if request.method=='POST' and request.form["submit"]=="refresh_logs":
        res = request.form["resolution"]
    else:
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
                data_collection.add_Twirp_to_Twirps(name, handle,-1)
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