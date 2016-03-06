

from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
import logging


from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from archipelago import Archipelago, setup
from twirps import data_collection, app
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



def set_up_logging():
    log_format = '%(asctime)s | %(lineno)-4d  %(name)-30s   %(levelname)8s  %(message)s'
    formatter = logging.Formatter(log_format,"%H:%M:%S %d/%m/%Y")
    cons_format = '%(asctime)s  %(filename)-20s l%(lineno)-d %(levelname)-8s  %(message)s'
    formatter_cons = logging.Formatter(cons_format,"%H:%M %d/%m")


    # fh_twirp = logging.FileHandler('tmp/twirps.log', mode='w')
    # fh_twirp.setLevel(logging.DEBUG)
    # fh_twirp.setFormatter(formatter)
    
    # fh_total = logging.FileHandler('tmp/twirps.verbose.log', mode='w')
    # fh_total.setLevel(logging.DEBUG)
    # fh_total.setFormatter(formatter)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter_cons)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    # root_logger.addHandler(fh_total)
    
    logger = logging.getLogger('twirps')
    # logger.addHandler(fh_twirp)
    logger.addHandler(ch)

@manager.command
def init_pg_db():
    db_handler = TDBHandler()
    db_handler.create_pg_tables()

@manager.command
def remove_pg_db():
    db_handler = TDBHandler()
    db_handler.drop_pg_tables()

@manager.command
def get_mps():
    db_handler = TDBHandler()
    print db_handler.get_stored_mps_names()

@manager.command
def init_neo_db():
    db_handler = NeoDBHandler()
    db_handler.init_constraints()

@manager.command
def remove_neo_db():
    db_handler = NeoDBHandler()
    db_handler.remove_constraints()

@manager.command
def init_dbs():
    init_pg_db()
    init_neo_db()




if __name__ == "__main__":
    
    set_up_logging()
    load_tweepy_key()
    if not setup.is_arch_setup():
        setup.setup_archipelago()

    app.config.from_pyfile('config.py', silent=True)
    
    LOGGER.info("Starting Flask app")
    manager.run()

    # arg_parser = build_parser()
    # opts = arg_parser.parse_args( sys.argv[1:] )
    # execute( opts )

    data_collection.stop_stream() 
    LOGGER.info("Shutting down.")
    logging.shutdown()

   




