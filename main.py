from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
import logging


from flask.ext.bootstrap import Bootstrap
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from archipelago import Archipelago, setup
from twirps import data_collection, app
from twirps.classes import TDBHandler




LOGGER = logging.getLogger('twirps.main')

DATABASE = '/twirpy.db'
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'



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


def build_parser():
    description = """
    Twirps Description here.
    """

    arg_parser = ArgumentParser( description )
    arg_parser.add_argument( '-r', '--reset',action='store_true', help="will completely reset the datebase")
    arg_parser.add_argument( '-t', '--twirps',action='store_true', help="get twirps")
    arg_parser.add_argument( '-d', '--data',action='store_true', help="get data")
    arg_parser.add_argument( '-u', '--update',action='store_true', help="get data")


    return arg_parser

def execute( options ):
    if options.reset:
        LOGGER.info("Rebooting database")
        db_handler = TDBHandler()
        db_handler.complete_reboot()


    if options.twirps:
        LOGGER.info("Collecting Twirps")
        session_api = data_collection.authorize_twitter()
        data_collection.get_twirps_main(session_api)

    if options.data:
        LOGGER.info("Collecting Data // Bulk Tweets")
        data_collection.get_tweets_main()

    if options.update:
        LOGGER.info("Updating most recent tweets")
        data_collection.update_from_tweet_stream()

    # 1. Collect twirps from ParlDB
    # 2. Collect twirps from JSON sent in
    # 3. Collect REST twirps data, with arguments
    # 4. Add to stream/New users
    # 5. Filter from stream users
    # 6. Serve logs



def set_up_logging():
    log_format = '%(asctime)s | %(lineno)-4d  %(name)-30s   %(levelname)8s  %(message)s'
    formatter = logging.Formatter(log_format,"%H:%M:%S %d/%m/%Y")
    cons_format = '%(asctime)s  %(filename)-20s l%(lineno)-d %(levelname)-8s  %(message)s'
    formatter_cons = logging.Formatter(cons_format,"%H:%M %d/%m")


    fh_twirp = logging.FileHandler('tmp/twirps.log', mode='w')
    fh_twirp.setLevel(logging.DEBUG)
    fh_twirp.setFormatter(formatter)
    
    fh_total = logging.FileHandler('tmp/twirps.verbose.log', mode='w')
    fh_total.setLevel(logging.DEBUG)
    fh_total.setFormatter(formatter)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter_cons)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(fh_total)
    
    logger = logging.getLogger('twirps')
    logger.addHandler(fh_twirp)
    logger.addHandler(ch)



if __name__ == "__main__":
    set_up_logging()

    load_tweepy_key()
    if not setup.is_arch_setup():
        setup.setup_archipelago()

    app.config.from_object(__name__)
    app.config.from_pyfile('config.py')
    
    LOGGER.info("Starting Flask app")
    bootstrap = Bootstrap(app)

    app.run()

    # arg_parser = build_parser()
    # opts = arg_parser.parse_args( sys.argv[1:] )
    # execute( opts )

    data_collection.stop_stream() 
    LOGGER.info("Shutting down.")
    logging.shutdown()

   




