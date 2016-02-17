import sqlite3
import os
import logging


LOGGER = logging.getLogger(__name__)

class TDBHandler(object):
    def __init__(self, db_name='twirpy.db'):
        self.db_name = db_name
        LOGGER.debug("Create TDBHandler: %s" % self.db_name )


    def is_db_setup(self ):
        return os.path.isfile(self.db_name)

    def complete_reboot(self):
        if self.is_db_setup():
            os.remove(self.db_name)
        self.create_twirpy_db()

    def create_twirpy_db(self):
        '''Creates a database with tables for TweetData and TwirpData'''

        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('CREATE TABLE TweetData (UserID Number, UserHandle Text, FavouriteCount Number, \
                                                RetweetCount Number, Content Text, Retweet Text, \
                                                CreatedDate Text, TwitterID Number UNIQUE)')
            cur.execute('CREATE TABLE TwirpData (UserID Number UNIQUE, UserName Text, Name Text, Handle Text, \
                                                FollowersCount Number, FriendsCount Number,\
                                                TweetCount Number, RetweetCount Number, \
                                                BeenRetweeted Number, FavouriteHashtag Text, \
                                                HashtagCount Number, OfficialId Number)')
            cur.execute('CREATE TABLE TweetEntities (TweetID Number, UserID Number,\
                                                EntityType Text, Entity Text, ToUser Number,\
                                                UrlBase Text, UNIQUE(TweetID, UserID, EntityType, Entity) )')

            cur.execute('CREATE INDEX UserIDIndex ON TweetData (UserID)')
            cur.execute('CREATE INDEX UserIDEntityIndex ON TweetEntities (UserID)')
        LOGGER.debug("Created twirpy database, name: %s" % self.db_name )

    def add_Twirp_to_database(self, Twirp):

        input_tuple =  (Twirp.id, Twirp.username, Twirp.name, Twirp.handle, Twirp.followers_count, 
                        Twirp.friends_count, Twirp.statuses, Twirp.retweet_count, 
                        Twirp.been_retweet_count, Twirp.favourite_hashtag,
                        Twirp.hashtag_count, Twirp.official_id)

        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TwirpData\
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ', input_tuple)

    def add_Tweet_to_database(self, Tweet):
        input_tuple = (Tweet.userid, Tweet.handle,  Tweet.favourite_count, Tweet.retweet_count,
            Tweet.content, Tweet.retweet,  Tweet.date, Tweet.tweetid )

        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TweetData\
                        VALUES (?,?,?,?,?,?,?,?) ', input_tuple)
            for h in Tweet.hashtags:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (Tweet.tweetid, Tweet.userid, 'hashtag', h))
            for u in Tweet.urls:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (Tweet.tweetid, Tweet.userid, 'url', u))
            for m in Tweet.mentions:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,?,NULL)',
                    (Tweet.tweetid, Tweet.userid, 'mention', m[1], m[0]))


    def get_stored_mps_names(self):
        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('SELECT  Name  FROM TwirpData')

        return [ name[0] for name in cur.fetchall() ]

    def get_oldest_tweets_stored_from_mps(self):
        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('''SELECT COUNT(tweet.TwitterID), MIN(tweet.TwitterID), 
                                twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
                            FROM TwirpData AS twirp
                            LEFT JOIN  TweetData AS tweet
                            ON twirp.UserID=tweet.UserID
                            GROUP BY twirp.Name
                            ORDER BY twirp.Name
                            ''')
    
        return [ 
                    {
                        "name": r[3] ,
                        "handle": r[4] , 
                        "no_tweets": r[5],
                        "oldest": r[1],
                        'no_collected': r[0], 
                        "u_id": r[2]

                    } for r in cur.fetchall()
                ]

    def get_newest_tweets_from_mps(self):
        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute('''SELECT COUNT(tweet.TwitterID), MAX(tweet.TwitterID), 
                                twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
                            FROM TwirpData AS twirp
                            LEFT JOIN  TweetData AS tweet
                            ON twirp.UserID=tweet.UserID
                            GROUP BY twirp.Name
                            ORDER BY twirp.Name
                            ''')
        return [ 
                    {
                        "name": r[3] ,
                        "handle": r[4] , 
                        "no_tweets": r[5],
                        "newest": r[1],
                        'no_collected': r[0], 
                        "u_id": r[2]

                    } for r in cur.fetchall()
                ]



