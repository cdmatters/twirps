from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
import logging


from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash


from twirps import data_collection, app, commands as cmds
from twirps.classes import TDBHandler, NeoDBHandler


LOGGER = logging.getLogger('twirps.main')

bootstrap = Bootstrap(app)
manager = Manager(app)

def load_tweepy_key():
    tweepy_help_1 = '''
    Twirps requires four API keys to collect data from twitter:
    These can be obtained at https://dev.twitter.com/
    Please enter:
        1: Consumer Key: '''
    tweepy_help_2 = '''
        2: Consumer Secret: '''
    tweepy_help_3 = '''
        3: Access Token: '''
    tweepy_help_4 = '''
        4: Access Secret: '''

    consumer_key = os.environ.get('TWEEPY_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWEEPY_CONSUMER_SECRET')
    access_token =  os.environ.get('TWEEPY_ACCESS_TOKEN')
    access_secret = os.environ.get('TWEEPY_ACCESS_SECRET')

    if not (consumer_key or consumer_secret or access_secret or access_secret):
        env_vars = []
        if os.path.isfile('tweepy.key'):
            LOGGER.debug('Found tweepy key')
            with open('tweepy.key', 'r') as f:
                for line in  f.read().splitlines():
                    env_vars.append(line)
        else:
            LOGGER.debug('No tweepy key found. Gettin raw input...')
            env_vars.append( raw_input( tweepy_help_1 ) ) 
            env_vars.append( raw_input( tweepy_help_2 ) ) 
            env_vars.append( raw_input( tweepy_help_3 ) ) 
            env_vars.append( raw_input( tweepy_help_4 ) ) 
            with open('tweepy.key', 'w') as f:
                LOGGER.debug('Writing tweepy key')
                for var in env_vars:
                    f.write( var + "\n" )

        os.environ["TWEEPY_CONSUMER_KEY"] = env_vars[0]
        os.environ["TWEEPY_CONSUMER_SECRET"] = env_vars[1]
        os.environ["TWEEPY_ACCESS_TOKEN"] = env_vars[2]
        os.environ["TWEEPY_ACCESS_SECRET"] = env_vars[3]
        LOGGER.debug('ENV variables set.')



def set_up_logging(this_app):
    log_format = '%(asctime)s | %(lineno)-4d  %(name)-30s   %(levelname)8s  %(message)s'
    formatter = logging.Formatter(log_format,"%H:%M:%S %d/%m/%Y")
    cons_format = '%(asctime)s  %(filename)-20s l%(lineno)-d %(levelname)-8s  %(message)s'
    formatter_cons = logging.Formatter(cons_format,"%H:%M %d/%m")


    fh_twirp = logging.FileHandler('twirps.log', mode='w')
    fh_twirp.setLevel(logging.DEBUG)
    fh_twirp.setFormatter(formatter)
    
    fh_total = logging.FileHandler('twirps.verbose.log', mode='w')
    fh_total.setLevel(logging.DEBUG)
    fh_total.setFormatter(formatter)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter_cons)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(fh_total)
    
    this_app.logger.addHandler(fh_twirp)
    this_app.logger.addHandler(ch)


@manager.command
def initialise_databases():
    cmds.initialise_databases()

@manager.command
def destroy_databases():
    cmds.destroy_databases()

@manager.command
def start_streamer():
    cmds.start_streamer()

@manager.command
def stop_streamer():
    cmds.stop_streamer()

@manager.command
def start_bulk_historical_collection():
    cmds.start_bulk_historical_collection()

@manager.command
def stop_bulk_historical_collection():
    cmds.stop_bulk_historical_collection()

@manager.command
def load_passive_twirps_to_database_by_handle():
    cmds.load_passive_twirps_to_database_by_handle()

@manager.command
def load_active_twirps_to_database_by_handle():
    cmds.load_active_twirps_to_database_by_handle()

@manager.command
def load_mp_twirps_to_database():
    cmds.load_mp_twirps_to_database()

@manager.command
def start_bulk_recent_collection():
    cmds.start_bulk_recent_collection()

@manager.command
def storp_bulk_recent_collection():
    cmds.storp_bulk_recent_collection()

@manager.command
def delete_data():
    cmds.delete_data()

@manager.command
def initialise_postgres_db():
    cmds.initialise_postgres_db()

@manager.command
def drop_postgres_db():
    cmds.drop_postgres_db()

@manager.command
def initialise_neo_db():
    cmds.initialise_neo_db()

@manager.command
def drop_neo_db():
    cmds.drop_neo_db()

@manager.command
def sync_subscribers_from_twitter():
    cmds.sync_subscribers_from_twitter()

@manager.command
def sync_subcribers_to_twitter():
    cmds.sync_subcribers_to_twitter()

@manager.command
def subscribe_all_twirps_to_twitter():
    cmds.subscribe_all_twirps_to_twitter()

set_up_logging(app)
if __name__ == "__main__":
    
    load_tweepy_key()


    app.config.from_pyfile('config.py', silent=True)
    
    LOGGER.info("Starting Flask app")
    manager.run()

    # arg_parser = build_parser()
    # opts = arg_parser.parse_args( sys.argv[1:] )
    # execute( opts )

    data_collection.stop_stream() 
    LOGGER.info("Shutting down.")
    logging.shutdown()

   




