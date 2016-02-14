#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.

from __future__ import unicode_literals
from archipelago import Archipelago
import sqlite3
import requests
import time, json, os, sys
import tweepy

from twirp import Twirp
from tweet import Tweet

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

    consumer_key = os.environ.get('TWEEPY_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWEEPY_CONSUMER_SECRET')
    access_token =  os.environ.get('TWEEPY_ACCESS_TOKEN')
    access_secret = os.environ.get('TWEEPY_ACCESS_SECRET')
   

    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

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


