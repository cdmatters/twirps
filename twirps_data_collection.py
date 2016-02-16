#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.

from __future__ import unicode_literals
from archipelago import Archipelago
import sqlite3
import requests
import datetime, json, os, sys, time
import tweepy
from tqdm import tqdm

from twirps_classes import Twirp, Tweet, TDBHandler

START_TIME = time.time()

def authorize_twitter():
    '''Authorizes the session for access to twitter API'''

    consumer_key = os.environ.get('TWEEPY_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWEEPY_CONSUMER_SECRET')
    access_token =  os.environ.get('TWEEPY_ACCESS_TOKEN')
    access_secret = os.environ.get('TWEEPY_ACCESS_SECRET')

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth)
    return api 

def get_Twirp_from_twitter(api, handle, official_id):
    '''Feeding in the session, a handle and it's mp's official id, this queries the
the twitter API, instantiates Twirp class with the data and return it'''
    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')
    twirp.official_id = official_id

    return twirp

def get_twirps_main(api):
    db_handler = TDBHandler()
    stored_mps = db_handler.get_stored_mps_names()

    # NOTE: only place Archipelago called in collection. 
    # Can sub in for custom twitter users json, with new TDB?
    arch = Archipelago()
    complete_mp_list = arch.get_twitter_users()

    mps_to_fetch = filter(lambda x: x["name"] not in set(stored_mps), complete_mp_list)

    for mp in tqdm(mps_to_fetch):
        try:
        
            mp_twirp = get_Twirp_from_twitter(api, mp["handle"], mp["o_id"])
            mp_twirp.name = mp["name"]
            db_handler.add_Twirp_to_database( mp_twirp )

        except tweepy.error.RateLimitError, e:
            print "Twitter API usage rate exceeded. Waiting 15 mins..."
            time.sleep(60*15)
            continue

        except tweepy.error.TweepError, e:
            print "ERROR: %s: for %s -> %s" % (e.message[0]["message"],
                                                mp["handle"],
                                                mp["name"])

def get_Tweets_from_twitter(api, user_id, max_id=None, no_of_items=3200):
    '''Feeding in the session, a user_id and possibly tweet id, this queries the 
twitter API, and providesa a generator yielding instantiated a Tweet classes with that data '''

    for tweet_data in tweepy.Cursor(api.user_timeline, id=user_id, max_id=max_id).items(no_of_items):   
        tweet = Tweet(tweet_data, 'twitter')
        yield tweet


def get_tweets_main(max_tweets=1000, tweet_buffer=30):
    db_handler = TDBHandler()

    api = authorize_twitter()
    stored_tweet_data = db_handler.get_tweets_stored_from_mps()

    def _is_to_be_collected(twirp):
        return ( (twirp["no_tweets"]-twirp["no_collected"])  > tweet_buffer  
                    and twirp["no_collected"] < (max_tweets - tweet_buffer) )

    for twirp in tqdm(stored_tweet_data):
        try:
            if _is_to_be_collected(twirp):
                remaining_tweets = max_tweets - twirp["no_collected"]
                    
                for Tweet in tqdm( get_Tweets_from_twitter(api, twirp["u_id"],
                                        twirp["earliest"], remaining_tweets), nested=True, desc="Getting %s -> %s" %(twirp["name"], twirp["handle"])):
                    db_handler.add_Tweet_to_database(Tweet)
                    #print unicode(Tweet)
            else:
                continue

        except tweepy.error.TweepError, e:
            print "Rate Limit Exceeded: Sleeping for 15 mins", datetime.datetime.utcnow()
            time.sleep(60*15)

            api = authorize_twitter()
            continue


def lap_time():
    '"a glance at the wristwatch" since the program started'
    lap = time.time()
    print '---%s s ---' %(START_TIME-lap)
    return time.time()


