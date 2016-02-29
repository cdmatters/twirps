#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.

from __future__ import unicode_literals
import datetime
import json
import os
import sys
import time
import logging
import sqlite3

from tweepy.error import RateLimitError, TweepError
from tqdm import tqdm
import tweepy
import requests

from decorators import async

from archipelago import Archipelago
from classes import Twirp, Tweet, TDBHandler, TweetStreamer

TWIRP_STREAM = None
TWEET_STREAMER = None

START_TIME = time.time()
LOGGER = logging.getLogger(__name__)
API = None

################################################################################
#                             TWITTER METHODS                                  #
################################################################################


def authorize_twitter():
    '''Authorizes the session for access to twitter API, and sets to the global variable API. NEED TO IMPLEMENT IF TIMEOUT, REAUTH
    '''
    global API
    if not API:
        LOGGER.debug("Authorizing Twitter api...")
        consumer_key = os.environ.get('TWEEPY_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWEEPY_CONSUMER_SECRET')
        access_token =  os.environ.get('TWEEPY_ACCESS_TOKEN')
        access_secret = os.environ.get('TWEEPY_ACCESS_SECRET')

        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        API = tweepy.API(auth, timeout=10, wait_on_rate_limit_notify=True, wait_on_rate_limit=True)
        return API
    else:
        return API

def get_Twirp_from_twitter(handle):
    '''Return a Twirp object from twitter handle.

    Feeding in the session, a handle and it's mp's official id, this queries 
    the twitter API, instantiates Twirp class with the data and return it. 
    It does not check if a user exists first.
    '''
    api = authorize_twitter()
    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')

    return twirp

def get_Tweets_from_twitter(user_id, max_id=None, no_of_items=3200):
    '''A generator yielding Tweet objects, from newest to oldest, up to no_of_items,
    starting at max_id. Takes a session and a user_id and uses the Twitter REST api.
     '''
    api = authorize_twitter()
    for tweet_data in tweepy.Cursor(api.user_timeline, id=user_id, max_id=max_id).items(no_of_items):   
        tweet = Tweet(tweet_data, 'twitter')
        yield tweet

def get_subscribers_from_twitter():
    '''Return a list of people currently subscribed from twitter'''
    api = authorize_twitter()
    return api.friends_ids()

def subscribe_twirp_from_twitter(twirp_id, twirp_handle):
    api = authorize_twitter()
    try:
        LOGGER.debug("Attempting to follow user no: %s" %twirp_id)
        api.create_friendship(user_id=unicode(twirp_id))
        return True

    except tweepy.error.TweepError, e:
        if "You've already requested to follow" in e.message[0]:
            LOGGER.error( "%s: for %s -> %s" % (e.message[0], twirp_id,
                                        twirp_handle) ) 
        else: 
            LOGGER.error(e.message[0])
        return False
            
def unsubscribe_twirp_from_twitter(twirp_id, twirp_handle):
    api = authorize_twitter()
    try:
        api.destroy_friendship(user_id=unicode(twirp_id))
        LOGGER.debug("Attempting to unfollow user no: %s" %twirp_id)
        return True

    except tweepy.error.TweepError, e:
        if "You've already requested to follow" in e.message[0]:
            LOGGER.error( "%s: for %s -> %s" % (e.message[0], twirp_id,
                                        twirp_handle) )
        else:
            LOGGER.error(e.message[0])
        return False
            

################################################################################
#                            DB AUXILIARY METHODS                              #
################################################################################



def get_user_data_from_identifiers(u_ids=[], handles=[], names=[], usernames=[]):
    '''Return a list of dicts of all basic twirp data {name, username, handle, u_id} 
    for any Twirps matching any of the lists of u_ids, handles, names, usernames.

    If none found return empty list. If empty args, return all results.
    '''

    db_handler = TDBHandler()
    return db_handler.get_user_data_from_identifiers(u_ids, handles,
                                                     names, usernames)


def add_Twirp_to_Twirps(name, handle, official_id=0):
    ''' Take a name, handle and official id, and create a Twirp from twitter data
    using the handle, and name and official id. Store this in the database.

    WARNING: No error currently if handle is not valid.
    '''
    api = authorize_twitter()
    db_handler = TDBHandler()
    mp_twirp = get_Twirp_from_twitter(handle)

    mp_twirp.official_id = official_id
    mp_twirp.name = name
    
    db_handler.add_Twirp_to_database( mp_twirp )

def delete_Twirp(name, username, handle,u_id):
    '''
    Attempt to remove twirp from database, and return the number of rows affected.
    All criteria (name, username, handle, u_id) must be accurate or deletion will
    not happen.

    Log a warning if no row is deleted.
    '''
    db_handler = TDBHandler()
    effects = db_handler.delete_twirp(u_id, handle, name, username) 
    if effects == 0:
        LOGGER.warning("No item deleted: (Name) %s -> %s" % (name, handle) )
    return effects


def subscribe_Twirp(name, handle, u_id):
    db_handler = TDBHandler()
    res = subscribe_twirp_from_twitter(u_id, handle)
    if res:
        db_handler.mark_twirp_subscribed(u_id)
        return 1
    else:
        return 0

def unsubscribe_Twirp(name, handle, u_id):
    db_handler = TDBHandler()
    res = unsubscribe_twirp_from_twitter(u_id, handle)
    if res:
        db_handler.mark_twirp_unsubscribed(u_id)
        return 1
    else:
        return 0

################################################################################
#                             BULK UPDATE METHODS                              #
################################################################################

@async
def get_bulk_twirps_main():
    api = authorize_twitter()

    db_handler = TDBHandler()
    stored_mps = db_handler.get_stored_mps_names()

    # NOTE: only place Archipelago called in collection. 
    # Can sub in for custom twitter users json, with new TDB?
    arch = Archipelago()
    complete_mp_list = arch.get_twitter_users()

    mps_to_fetch = filter(lambda x: x["name"] not in set(stored_mps), complete_mp_list)

    for mp in tqdm(mps_to_fetch):
        try:
            add_Twirp_to_Twirps(mp["name"], mp["handle"], mp["o_id"])
        
        except RateLimitError, e:
            LOGGER.warning("Twitter API usage rate exceeded. Waiting 15 mins...")
            time.sleep(60*5)
            LOGGER.info("10 mins remaining...")

            api = authorize_twitter()
            continue

        except tweepy.error.TweepError, e:
            LOGGER.error( "ERROR: %s: for %s -> %s" % (e.message[0]["message"],
                                                mp["handle"],
                                                mp["name"]))

@async
def get_bulk_tweets_main(max_tweets=100, tweet_buffer=30):
    db_handler = TDBHandler()

    api = authorize_twitter()
    stored_tweet_data = db_handler.get_oldest_tweets_stored_from_mps()

    def _is_to_be_collected(twirp):
        return ( (twirp["no_tweets"]-twirp["no_collected"])  > tweet_buffer  
                    and twirp["no_collected"] < (max_tweets - tweet_buffer) )

    for twirp in tqdm(stored_tweet_data):
        try:
            if _is_to_be_collected(twirp):
                remaining_tweets = max_tweets - twirp["no_collected"]
                
                pbar_description = "Getting %s -> %s" %(twirp["name"], twirp["handle"])
                for Tweet in tqdm( get_Tweets_from_twitter(twirp["u_id"],
                                                           twirp["oldest"], remaining_tweets),
                                    nested=True, desc=pbar_description):
                    LOGGER.debug(unicode(Tweet))
                    db_handler.add_Tweet_to_database(Tweet)
            else:
                continue

        except tweepy.error.TweepError, e:
            LOGGER.warning(e)
            LOGGER.warning("Twitter API usage rate exceeded. Waiting 15 mins...")
            time.sleep(60*10)
            LOGGER.info("5 mins remaining...")
            time.sleep(60*5)

            api = authorize_twitter()
            continue

def get_bulk_twirps_update():
    pass

@async
def get_bulk_recent_tweet(max_tweets=10):
    db_handler = TDBHandler()
    stored_tweet_data = db_handler.get_newest_tweets_from_mps()

    api = authorize_twitter()
    for twirp in stored_tweet_data:
        try:
            current_tweet = twirp["newest"]
            no_collected = 0
            tweet_generator = get_Tweets_from_twitter(api, twirp["u_id"], None, max_tweets)
            while no_collected < max_tweets and current_tweet >= twirp['newest']:
                Tweet = tweet_generator.next()
                db_handler.add_Tweet_to_database(Tweet)
                no_collected += 1
                current_tweet = Tweet.tweetid
                LOGGER.debug(unicode(Tweet))
        
        except tweepy.error.TweepError, e:
            LOGGER.warning(e)
            LOGGER.warning("Twitter API usage rate exceeded. Waiting 15 mins...")
            time.sleep(60*10)
            LOGGER.info("5 mins remaining...")
            time.sleep(60*5)

            api = authorize_twitter()
            continue

@async
def subscribe_friends_from_twirps():
    db_handler = TDBHandler()
    currently_following =  set(get_subscribers_from_twitter())

    for twirp in db_handler.get_user_ids_from_handles():

        if twirp["u_id"] not in currently_following:
            subscribe_twirp_from_twitter(twirp["u_id"])





################################################################################
#                            STREAM UPATE METHODS  (see tweetstreamer.py)      #
################################################################################


def start_stream():
    ''' Build the TweetStreamer and the Stream , and connect to add data to database
    from Twitter.

    Print to logs if no stream is up.
    '''
    db_handler = TDBHandler()
    api = authorize_twitter()

    global TWIRP_STREAM
    global TWEET_STREAMER

    if not TWEET_STREAMER:
        TWEET_STREAMER = TweetStreamer(api, db_handler)
        LOGGER.debug("Built TweetStreamer")
    
    if not TWIRP_STREAM:
        TWIRP_STREAM = tweepy.Stream(auth = api.auth, listener=TWEET_STREAMER)
        TWIRP_STREAM.userstream(replies='all', async=True)
        LOGGER.debug("Started Streaming thread.")
    else:
        LOGGER.warning("Global stream already up.")
    
def stop_stream():
    ''' Destroy the TweetStreamer and disconnect the Stream if up and running.

    Print to logs if no stream is up.
    '''
    global TWIRP_STREAM
    if TWIRP_STREAM:
        TWIRP_STREAM.disconnect()
        LOGGER.debug("Stopped Streaming thread.")
        TWIRP_STREAM = None
        TWEET_STREAMER = None
    else:
        LOGGER.warning("No stream is up.")

def change_stream_resolution(res):
    '''Change resolution of tweets in logs from TweetStreamer.

    Resolution: res -> (x mod res == 0 are printed to logs) 
    Print to logs if no streamer.
    '''
    global TWEET_STREAMER
    if TWEET_STREAMER:
        TWEET_STREAMER.set_stream_resolution(int(res))
        new_res = TWEET_STREAMER.get_stream_resolution()
        LOGGER.debug("Changed stream resolution to %s" % new_res)
    else:
        LOGGER.debug("No tweet streamer")

def get_stream_resolution():
    '''Return resolution of tweets in logs from TweetStreamer.

    Resolution: res -> (x mod res == 0 are printed to logs) 
        Resolution: res -> (x mod res == 0 are printed to logs) 
    Print to logs if no streamer.
    '''
    global TWEET_STREAMER
    if TWEET_STREAMER:
        res = TWEET_STREAMER.get_stream_resolution()
        return res
    else:
        LOGGER.debug("No tweet streamer")




