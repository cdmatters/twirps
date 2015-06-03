#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.
from __future__ import unicode_literals
import sqlite3
import requests
import time, json, os, sys
import tweepy
import tweepy_key as tk

START_TIME = time.time()

def create_twirpy_db():
    '''Creates a database with tables for TweetData and TwirpData'''
    
    if not os.path.exists('./twirpy.db'):
        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('CREATE TABLE TweetData (UserID Number, UserHandle Text, FavouriteCount Number, \
                                                RetweetCount Number, Content Text, Retweet Text, \
                                                CreatedDate Text, TwitterID Number UNIQUE)')
            cur.execute('CREATE TABLE TwirpData (UserID Number UNIQUE, UserName Text, Handle Text, \
                                                FollowersCount Number, FriendsCount Number,\
                                                TweetCount Number, RetweetCount Number, \
                                                BeenRetweeted Number, FavouriteHashtag Text, \
                                                HashtagCount Number, OfficialId Number)')
            cur.execute('CREATE TABLE TweetEntities (TweetID Number, UserID Number,\
                                                EntityType Text, Entity Text, ToUser Number,\
                                                UrlBase Text, UNIQUE(TweetID, UserID, EntityType, Entity) )')

            cur.execute('CREATE INDEX UserIDIndex ON TweetData (UserID)')
            cur.execute('CREATE INDEX UserIDEntityIndex ON TweetEntities (UserID)')

def authorize_twitter():
    '''Authorizes the session for access to twitter API'''

    auth = tweepy.auth.OAuthHandler(tk.consumer_key, tk.consumer_secret)
    auth.set_access_token(tk.access_token, tk.access_secret)

    api = tweepy.API(auth)
    return api 


def return_twitter_list():
    '''Returns a list of tuples, each containing an MPs OfficialId and Twitter handle'''

    with sqlite3.connect('../parl.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT OfficialId, Address FROM Addresses WHERE Type="Twitter"')
        tuplelist = cur.fetchall()
    complete_mp_list = [(o_id, handle[20:]) for o_id, handle in tuplelist]
    return complete_mp_list

def return_skip_list():
    '''Returns a list of tuples, each containing OfficialId and Twitter handle for 
Twirps that have already been collected'''

    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT OfficialId, Handle FROM TwirpData')
        tuplelist = cur.fetchall()
    return tuplelist


def collect_twirp_data(api, handle, official_id):
    '''Feeding in the session, a handle and it's mp's official id, this queries the
the twitter API, instantiates Twirp class with the data and populates the database 
with that record'''

    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')
    twirp.official_id = official_id

    print unicode(twirp)
    twirp.to_database()

def collect_tweet_data(api, user_id, max_id=None, no_of_items=3200):
    '''Feeding in the session, a user_id and possibly tweet id, this queries the 
twitter API, instantiates a Tweet class with data and populates the database with 
that tweet'''

    for tweet_data in tweepy.Cursor(api.user_timeline, id=user_id, max_id=max_id).items(no_of_items):

        tweet = Tweet(tweet_data, 'twitter')
        tweet.to_database()
        try:
            print tweet, '\n'
        except:
            continue

def lap_time():
    '"a glance at the wristwatch" since the program started'
    lap = time.time()
    print '---%s s ---' %(START_TIME-lap)
    return time.time()


def return_list_for_tweet_scan():
    to_do_list = []
    with sqlite3.connect('twirpy.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT UserID, TweetCount FROM TwirpData')
        twirp_list = cur.fetchall()
        lap_time()

        for i, (twirp_tuple) in enumerate(twirp_list):

            cur.execute('SELECT COUNT(TwitterID) FROM TweetData WHERE UserID =?',
                (twirp_tuple[0],))
            records = cur.fetchall()

            cur.execute('SELECT MIN(TwitterID) FROM TweetData WHERE UserID=?',
                (twirp_tuple[0],))
            start_point= cur.fetchall()
            if i%2==0:
                print 'Analysed %d records\r' %i,


            if (twirp_tuple[1]-records[0][0]>30) and records[0][0]<3100:
                remaining = 3200-records[0][0]

                to_do_list.append((twirp_tuple[0], remaining, start_point[0][0]))

        print

    return to_do_list



def get_twirps_main(api):
    complete_mp_list = return_twitter_list()
    fetched_mp_list = return_skip_list()

    remaining_mp_list = list(set(complete_mp_list)-set(fetched_mp_list))

    print remaining_mp_list 

    for mp_tuple in remaining_mp_list:
        try:
            collect_twirp_data(api, mp_tuple[1], mp_tuple[0])
        except Exception, e:
            print e

def get_tweets_main():
    
    while True:
        api = authorize_twitter()
        try:
            to_do = return_list_for_tweet_scan()

            for target in to_do:
                print target
                collect_tweet_data(api, target[0], no_of_items=target[1], max_id=target[2])
        except Exception, e:
            print e
            time.sleep(15*60)
            continue



        
class Tweet(object):
    def __init__(self, tweet, source):
        self.tweetid = 0
        self.userid = 0
        self.handle = ''
        self.mentions = [] 
        self.content = ''
        self.retweet = 'NULL'
        self.retweet_count = 0
        self.favourite_count = 0
        self.hashtags = []
        self.date = ''
        self.urls = []

        if source=='twitter':
            self.from_twitter(tweet)

        elif source=='database':
            self.from_database(tweet)

    def from_twitter(self, tweet):
        self.tweetid  = tweet.id
        self.userid = tweet.user.id
        self.handle = tweet.user.screen_name
        self.date = tweet.created_at
        self.retweet_count = tweet.retweet_count
        self.favourite_count  = tweet.favorite_count
        
        if tweet.in_reply_to_user_id != None:
            #self.mentions.append((tweet.in_reply_to_user_id, tweet.in_reply_to_screen_name))
            self.retweet = 'REPLY'

        if hasattr(tweet, 'retweeted_status'):
            tweet = tweet.retweeted_status
            self.retweet = tweet.user.screen_name
            self.mentions.append((tweet.user.id, tweet.user.screen_name))

        self.content = tweet.text
        self.mentions = [ (ent['id'],ent['screen_name'] 
                            ) for ent in tweet.entities['user_mentions'] ]
        self.hashtags =  [ent['text'] for ent in tweet.entities['hashtags']]
        self.urls = [urls['expanded_url'] for urls in tweet.entities['urls']]


    def __str__(self):
        return u'Tweet %d %s || RC: %d || FC: %d || RT: %s || @ %s || # %s || Url %s\nContent: %s' %(
            self.tweetid, self.handle, self.retweet_count, self.favourite_count,
            self.retweet, len(self.mentions), len(self.hashtags), len(self.urls),
            unicode(self.content) )

    def from_database(self, tweet):
        pass

    def to_database(self):
        input_tuple = (self.userid, self.handle,  self.favourite_count, self.retweet_count,
            self.content, self.retweet,  self.date, self.tweetid )

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TweetData\
                        VALUES (?,?,?,?,?,?,?,?) ', input_tuple)
            for h in self.hashtags:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (self.tweetid, self.userid, 'hashtag', h))
            for u in self.urls:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (self.tweetid, self.userid, 'url', u))
            for m in self.mentions:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,?,NULL)',
                    (self.tweetid, self.userid, 'mention', m[1], m[0]))


class Twirp(object):
    def __init__(self, user, source):
        self.statuses = 0
        self.followers_count = 0
        self.friends_count = 0
        self.geo = False
        self.id = 0
        self.name = ''
        self.handle = ''
        self.official_id = 0 
        self.retweet_count = 0
        self.been_retweet_count = 0 
        self.favourite_hashtag = 'NULL'
        self.hashtag_count = 0

        if source=='twitter':
            self.from_twitter(user)

        elif source=='database':
            self.from_database(user)

    def __str__(self):
        return u'||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
            self.handle, self.name, self.id, 
            self.followers_count, self.friends_count, self.geo )

    def from_twitter(self, user ):
        self.statuses = user.statuses_count
        self.followers_count = user.followers_count
        self.friends_count = user.friends_count
        self.geo = user.geo_enabled
        self.id = user.id
        self.name = user.name
        self.handle = user.screen_name
        self.official_id = 0

    def to_database(self):
        input_tuple =  (self.id, self.name, self.handle, self.followers_count, 
                        self.friends_count, self.statuses, self.retweet_count, 
                        self.been_retweet_count, self.favourite_hashtag,
                        self.hashtag_count, self.official_id)

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TwirpData\
                        VALUES (?,?,?,?,?,?,?,?,?,?,?) ', input_tuple)


    def from_database(self, user):
        pass


def main():
    words = sys.argv
    if len(words) ==1:
        print 'print arg: [get_twirps, get_tweets]'
    elif words[1]=='get_twirps':
        session_api = authorize_twitter()
        get_tweets_main(session_api)
    elif words[1]=='get_tweets':
        get_tweets_main()
    elif words[1]=='to_do_list':
        print return_list_for_tweet_scan()
        lap_time()
    elif words[1]=='init_db':
        create_twirpy_db()



    else:
        print 'bad arguments'

if __name__ == '__main__':
    main()



# def pull_tweets_from_user(api, handle):
#     print handle
#     mp = api.get_user(screen_name=handle)
#     for status in tweepy.Cursor(api.user_timeline, id=mp.id).items(1000):
#         tweet_parser(status)

#         for mention in status.entities['user_mentions']:
#             print i, mention['screen_name'], '\t', status.text
    
#     time.sleep(45)


