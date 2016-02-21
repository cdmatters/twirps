import sqlite3
import logging

from flask import Blueprint, Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Response

from twirps import app, data_collection


LOGGER = logging.getLogger(__name__)

@app.route('/admin_login/', methods=['GET', 'POST'])
def view_backend():
    LOGGER.info("Loading backend")
    def read_log():
        for line in  open('./tmp/twirps.log', "r"):
            yield line
    return render_template('backend.html', rows=read_log())

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     pass

@app.route('/admin_login/start_stream', methods=['GET', 'POST'])
def add_twirp():
    LOGGER.info("Received start stream message")
    
    data_collection.start_stream()
    def read_log():
        for line in  open('./tmp/twirps.log', "r"):
            yield line
    return render_template('backend.html', rows=read_log())

@app.route('/admin_login/stop_stream', methods=['GET','POST'])
def stop_stream():
    LOGGER.info("Received stop stream message")
    
    data_collection.stop_stream()
    redirect('/admin_login/')
    def read_log():
        for line in  open('./tmp/twirps.log', "r"):
            yield line
    return render_template('backend.html', rows=read_log())


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('admin_login/shutdown', methods=['GET','POST'])
def shutdown():
    shutdown_server()
    LOGGER.info( 'Server shutting down...')