#Twirps is a visual mapping of how much MPs communicate with 
#each other on social media.  It will use the parl_db database, and its
#own twirpy.db for any extra data.

from __future__ import unicode_literals
from archipelago import Archipelago
import sqlite3
import requests
import time, json, os, sys
import tweepy

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
the twitter API, instantiates Twirp class with the data and populates the database 
with that record'''
    twitter_user = api.get_user(screen_name=handle)
    twirp = Twirp(twitter_user, 'twitter')
    twirp.official_id = official_id
    
    #print unicode(twirp)
    return twirp


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
    db_handler = TDBHandler()
    stored_mps = db_handler.get_stored_mps_names()

    arch = Archipelago()
    complete_mp_list = arch.get_twitter_users()

    print stored_mps

    mps_to_fetch = filter(lambda x: x["name"] not in set(stored_mps), complete_mp_list)

    for mp in mps_to_fetch:
        try:
        
            mp_twirp = get_Twirp_from_twitter(api, mp["handle"], mp["o_id"])
            mp_twirp.name = mp["name"]
            db_handler.add_Twirp_to_database( mp_twirp )

        except tweepy.error.TweepError, e:
            print "ERROR: %s: for %s -> %s" % (e.message[0]["message"],
                                                mp["handle"],
                                                mp["name"])

def get_tweets_main_():
    
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
        get_twirps_main(session_api)
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


