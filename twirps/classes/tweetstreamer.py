import sqlite3
import tweepy
from tweet import Tweet

class TweetStreamer(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        pass
        

    def on_status(self, status):
        tweet = Tweet(status, 'twitter')
        print unicode(tweet)


    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False