import sqlite3
import tweepy
from tweet import Tweet
import logging

LOGGER = logging.getLogger(__name__)
LOGGER_RESOLUTION = 5

class TweetStreamer(tweepy.StreamListener):
    def __init__(self, api, db_handler):
        self.api = api
        self.db_handler = db_handler
        self.counter = 0
        LOGGER.info("Instatiated TweetStreamer")
        pass
        
    def on_status(self, status):
        tweet = Tweet(status, 'twitter')
        self.store_tweet(tweet)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

    def store_tweet(self, tweet):
        self.db_handler.add_Tweet_to_database(tweet)
        if self.counter % LOGGER_RESOLUTION == 0:
            LOGGER.debug("Collected streamed tweet no %s\n%s" % (self.counter, unicode(tweet)))
        self.counter +=1

