from __future__ import unicode_literals
import os, sys
from argparse import ArgumentParser

from archipelago import Archipelago, setup
import twirps_data_collection as t_data_collect




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
            with open('tweepy.key', 'r') as f:
                for line in  f.read().splitlines():
                    env_vars.append(line)
        else:
            env_vars.append( raw_input( tweepy_help_1 ) ) 
            env_vars.append( raw_input( tweepy_help_2 ) ) 
            env_vars.append( raw_input( tweepy_help_3 ) ) 
            env_vars.append( raw_input( tweepy_help_4 ) ) 
            with open('tweepy.key', 'w') as f:
                for var in env_vars:
                    f.write( var + "\n" )

        os.environ["TWEEPY_CONSUMER_KEY"] = env_vars[0]
        os.environ["TWEEPY_CONSUMER_SECRET"] = env_vars[1]
        os.environ["TWEEPY_ACCESS_TOKEN"] = env_vars[2]
        os.environ["TWEEPY_ACCESS_SECRET"] = env_vars[3]


def build_parser():
    description = """
    Twirps Description here.
    """

    arg_parser = ArgumentParser( description )
    arg_parser.add_argument( '-i', '--init',action='store_true', help="initialise the database")
    arg_parser.add_argument( '-t', '--twirps',action='store_true', help="get twirps")


    return arg_parser

def execute( options ):
    if options.init:
        t_data_collect.create_twirpy_db()

    if options.twirps:
        session_api = t_data_collect.authorize_twitter()
        t_data_collect.get_twirps_main(session_api)




if __name__ == "__main__":
    load_tweepy_key()
    if not setup.is_arch_setup():
        setup.setup_archipelago()

    arg_parser = build_parser()
    opts = arg_parser.parse_args( sys.argv[1:] )

    execute( opts )

   




