import sqlite3
import os
import logging
import psycopg2


LOGGER = logging.getLogger(__name__)

class TDBHandler(object):
    def __init__(self, db_name=os.getenv('TWIRPS_DATABASE', './twirpy.db')):
        self.db_name = db_name
        self.pg_database = os.getenv('PG_DATABASE_URL',None)

    def create_pg_tables(self):
        sql_schema = '''CREATE TABLE TwirpData (  
                            UserID             BIGINT      NOT NULL  UNIQUE,
                            UserName           TEXT        NOT NULL,
                            Name               TEXT        NOT NULL,
                            Handle             TEXT        NOT NULL,
                            FollowersCount     INT,
                            FriendsCount       INT,
                            TweetCount         INT,
                            RetweetCount       INT,
                            BeenRetweetedCount INT,
                            FavouriteHashtag   TEXT,
                            HashtagCount       INT,
                            ArchipelagoID      INT,
                            TwirpsType         INT,
                            Subscribed         BOOLEAN  DEFAULT False,
                            PRIMARY KEY(UserID)
                        );
                        CREATE TABLE TweetData (
                            UserID             BIGINT      NOT NULL references TwirpData(UserID),
                            UserHandle         TEXT        NOT NULL references TwirpData(Handle),
                            FavouriteCount     INT,
                            RetweetCount       INT,
                            Content            TEXT,
                            Retweet            TEXT,
                            CreatedDate        TEXT,
                            TweetID            BIGINT      NOT NULL UNIQUE,
                            PRIMARY KEY(TweetID)
                        );
                        CREATE TABLE TweetEntities (
                            TweetID            BIGINT      NOT NULL references TweetData(TweetID),
                            UserID             BIGINT      NOT NULL references TwirpData(UserID),
                            EntityType         TEXT,
                            Entity             TEXT,
                            ToUser             BIGINT,
                            UrlBase            TEXT,
                            PRIMARY KEY(TweetID, UserID, EntityType, Entity) 
                        );

                        CREATE INDEX UserIDIndex ON TweetData (UserID);
                        CREATE INDEX UserHandleIDIndex ON TweetData (UserHandle);
                        CREATE INDEX UserIDEntityIndex ON TweetEntities (UserID);
                        '''
        with psycopg2.connect(self.pg_database) as connection: 
            cur = connection.cursor()
            cur.execute(sql_schema)                                       
        LOGGER.debug("Created PostGres tables, name at: %s" % self.pg_database )

    def drop_pg_tables(self):
        sql_schema = ''' DROP TABLE TweetEntities;
                         DROP TABLE TweetData;
                    '''
                         # DROP TABLE TwirpData;

        with psycopg2.connect(self.pg_database) as connection: 
            cur = connection.cursor()
            cur.execute(sql_schema)                                       
        LOGGER.debug("Dropped postgres tables, at: %s" % self.pg_database )

    def add_Twirp_to_database(self, twirp):
        sql_request = '''INSERT INTO TwirpData( 
                            UserID, UserName, Name, Handle,
                            FollowersCount, FriendsCount,
                            TweetCount, RetweetCount, BeenRetweetedCount,
                            FavouriteHashtag,HashtagCount,
                            ArchipelagoID,
                            TwirpsType,
                            Subscribed 
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (UserID)
                            DO UPDATE SET (
                                UserName, Name, Handle,
                                FollowersCount, FriendsCount,
                                TweetCount, RetweetCount, BeenRetweetedCount,
                                FavouriteHashtag,HashtagCount,
                                ArchipelagoID,
                                TwirpsType,
                                Subscribed
                            ) = (
                                EXCLUDED.UserName, EXCLUDED.Name, EXCLUDED.Handle,
                                EXCLUDED.FollowersCount, EXCLUDED.FriendsCount,
                                EXCLUDED.TweetCount, EXCLUDED.RetweetCount, EXCLUDED.BeenRetweetedCount,
                                EXCLUDED.FavouriteHashtag,EXCLUDED.HashtagCount,
                                EXCLUDED.ArchipelagoID,
                                EXCLUDED.TwirpsType,
                                EXCLUDED.Subscribed
                            );
        '''

        T=twirp
        input_tuple =  (T.id, T.username, T.name, T.handle,
                        T.followers_count, T.friends_count, 
                        T.tweet_count, T.retweet_count, T.been_retweet_count,
                        T.favourite_hashtag, T.hashtag_count, 
                        T.archipelago_id, 
                        T.twirps_type,
                        T.subscribed)

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(sql_request, input_tuple)

    def add_Tweet_to_database(self, tweet):
        add_tweet_sql= '''INSERT INTO TweetData(
                            TweetID,
                            UserID, UserHandle,
                            Retweet,
                            Content,
                            FavouriteCount, RetweetCount,
                            CreatedDate
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (TweetID)\
                            DO UPDATE SET (
                                UserID, UserHandle,
                                Retweet,
                                Content,
                                FavouriteCount, RetweetCount,
                                CreatedDate
                            ) = (
                                EXCLUDED.UserID, EXCLUDED.UserHandle,
                                EXCLUDED.Retweet,
                                EXCLUDED.Content,
                                EXCLUDED.FavouriteCount, EXCLUDED.RetweetCount,
                                EXCLUDED.CreatedDate
                            );'''

        add_entity_sql='''INSERT INTO TweetEntities(
                            TweetID, UserID, EntityType, Entity, ToUser
                        ) VALUES (%s,%s,%s,%s,%s)
                        ON CONFLICT (TweetID, UserID, EntityType, Entity)
                            DO UPDATE SET(
                                TweetID, UserID, EntityType, 
                                Entity, ToUser
                            )= (
                                EXCLUDED.TweetID, EXCLUDED.UserID, EXCLUDED.EntityType, 
                                EXCLUDED.Entity, EXCLUDED.ToUser
                            )'''

        t = tweet
        input_tuple = (t.tweetid,
                       t.userid, t.handle,
                       t.retweet,
                       t.content,   
                       t.favourite_count, t.retweet_count,
                       t.date)

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(add_tweet_sql, input_tuple)
            for h in t.hashtags:
                cur.execute(add_entity_sql, (t.tweetid, t.userid, 'hashtag', h, 0))
            for u in t.urls:
                cur.execute(add_entity_sql, (t.tweetid, t.userid, 'url', u, 0))
            for m in t.mentions:
                cur.execute(add_entity_sql, (t.tweetid, t.userid, 'mention', m[1], m[0]))

    def get_oldest_tweets_stored_from_mps(self):
        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute('''SELECT COUNT(tweet.TweetID), MIN(tweet.TweetID), 
                                twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
                            FROM TwirpData AS twirp
                            LEFT JOIN  TweetData AS tweet
                            ON twirp.UserID=tweet.UserID
                            GROUP BY twirp.UserID
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
        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute('''SELECT COUNT(tweet.TweetID), MAX(tweet.TweetID), 
                                twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
                            FROM TwirpData AS twirp
                            LEFT JOIN  TweetData AS tweet
                            ON twirp.UserID=tweet.UserID
                            GROUP BY twirp.UserID
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

    def get_stored_mps_names(self):
        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute('SELECT  Name  FROM TwirpData')

        return [ name[0] for name in cur.fetchall() ]

    def get_user_data_from_handles(self, handles=[]):
        '''Return a dictionary of handles and user_ids for given list of handles.
        Return all stored id's if handles is empty list'''
        request_sql = '''SELECT UserID, Handle, Name 
                            FROM TwirpData
                       '''
        if handles:
            q_marks = ','.join(['%s']*len(handles))
            request_sql += 'WHERE Handle IN (%s)' %q_marks

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, handles)

            return [
                        {
                            "u_id": r[0],
                            "handle": r[1],
                            "name":r[2]
                        } for r in cur.fetchall()
                    ]

    def get_user_data_from_identifiers(self, u_ids=[], handles=[], names=[], usernames=[]):
        '''Return a dictionary of handles and user_ids for given list of u_ids.
        Return all stored id's if u_ids is empty list'''
        request_sql = '''SELECT UserID, Handle, Name, UserName, Subscribed 
                            FROM TwirpData
                       '''
        filter_categories = []
        filter_args = []
        if u_ids:
            q_marks = ','.join(['%s']*len(u_ids))
            filter_categories.append('UserID IN (%s)' %q_marks)
            filter_args.extend(u_ids)
        if names:
            q_marks = ','.join(['%s']*len(names))
            filter_categories.append('Name IN (%s)' %q_marks)
            filter_args.extend(names)
        if handles:
            q_marks = ','.join(['%s']*len(handles))
            filter_categories.append('Handle IN (%s)' %q_marks)
            filter_args.extend(handles)
        if usernames:
            q_marks = ','.join(['%s']*len(usernames))
            filter_categories.append('UserName IN (%s)' %q_marks)
            filter_args.extend(usernames)

        if filter_categories:
            request_sql += ' WHERE ' 
            request_sql += ' OR '.join(filter_categories)

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, filter_args)

            return [
                        {
                            "u_id": r[0],
                            "handle": r[1],
                            "name":r[2],
                            "username": r[3],
                            "subscribed":r[4]
                        } for r in cur.fetchall()
                    ]

    def delete_twirp(self, u_id, handle, name, username):
        '''Return a dictionary of handles and user_ids for given list of u_ids.
        Return all stored id's if u_ids is empty list'''
        request_sql = '''DELETE FROM TwirpData 
                        WHERE UserID=%s
                            AND Handle =%s
                            AND Name=%s
                            AND UserName=%s;
                       '''

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id, handle, name, username))

          
            return cur.rowcount;


    def is_db_setup(self ):
        return os.path.isfile(self.db_name)

    def complete_reboot(self):
        if self.is_db_setup():
            os.remove(self.db_name)
        self.create_twirpy_db()

    # def create_twirpy_db(self):
    #     '''Creates a database with tables for TweetData and TwirpData'''

    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('CREATE TABLE TweetData (UserID Number, UserHandle Text, FavouriteCount Number, \
    #                                             RetweetCount Number, Content Text, Retweet Text, \
    #                                             CreatedDate Text, TwitterID Number UNIQUE)')
    #         cur.execute('CREATE TABLE TwirpData (UserID Number UNIQUE, UserName Text, Name Text, Handle Text, \
    #                                             FollowersCount Number, FriendsCount Number,\
    #                                             TweetCount Number, RetweetCount Number, \
    #                                             BeenRetweeted Number, FavouriteHashtag Text, \
    #                                             HashtagCount Number, OfficialId Number,\
    #                                             Subscribed Number default 0)')
    #         cur.execute('CREATE TABLE TweetEntities (TweetID Number, UserID Number,\
    #                                             EntityType Text, Entity Text, ToUser Number,\
    #                                             UrlBase Text, UNIQUE(TweetID, UserID, EntityType, Entity) )')

    #         cur.execute('CREATE INDEX UserIDIndex ON TweetData (UserID)')
    #         cur.execute('CREATE INDEX UserIDEntityIndex ON TweetEntities (UserID)')
    #     LOGGER.debug("Created twirpy database, name: %s" % self.db_name )

    # def _add_Twirp_to_database(self, Twirp):

    #     input_tuple =  (Twirp.id, Twirp.username, Twirp.name, Twirp.handle, Twirp.followers_count, 
    #                     Twirp.friends_count, Twirp.tweet_count, Twirp.retweet_count, 
    #                     Twirp.been_retweet_count, Twirp.favourite_hashtag,
    #                     Twirp.hashtag_count, Twirp.official_id)

    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('INSERT OR REPLACE INTO TwirpData\
    #                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0) ', input_tuple)

    # def _add_Tweet_to_database(self, Tweet):
    #     input_tuple = (Tweet.userid, Tweet.handle,  Tweet.favourite_count, Tweet.retweet_count,
    #         Tweet.content, Tweet.retweet,  Tweet.date, Tweet.tweetid )

    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('INSERT OR REPLACE INTO TweetData\
    #                     VALUES (?,?,?,?,?,?,?,?) ', input_tuple)
    #         for h in Tweet.hashtags:
    #             cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
    #                 (Tweet.tweetid, Tweet.userid, 'hashtag', h))
    #         for u in Tweet.urls:
    #             cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
    #                 (Tweet.tweetid, Tweet.userid, 'url', u))
    #         for m in Tweet.mentions:
    #             cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,?,NULL)',
    #                 (Tweet.tweetid, Tweet.userid, 'mention', m[1], m[0]))


    # def _get_stored_mps_names(self):
    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('SELECT  Name  FROM TwirpData')

    #     return [ name[0] for name in cur.fetchall() ]

    # def _get_oldest_tweets_stored_from_mps(self):
    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('''SELECT COUNT(tweet.TwitterID), MIN(tweet.TwitterID), 
    #                             twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
    #                         FROM TwirpData AS twirp
    #                         LEFT JOIN  TweetData AS tweet
    #                         ON twirp.UserID=tweet.UserID
    #                         GROUP BY twirp.Name
    #                         ORDER BY twirp.Name
    #                         ''')
    
    #     return [ 
    #                 {
    #                     "name": r[3] ,
    #                     "handle": r[4] , 
    #                     "no_tweets": r[5],
    #                     "oldest": r[1],
    #                     'no_collected': r[0], 
    #                     "u_id": r[2]

    #                 } for r in cur.fetchall()
    #             ]

    # def _get_newest_tweets_from_mps(self):
    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute('''SELECT COUNT(tweet.TwitterID), MAX(tweet.TwitterID), 
    #                             twirp.UserID, twirp.Name, twirp.Handle, twirp.TweetCount 
    #                         FROM TwirpData AS twirp
    #                         LEFT JOIN  TweetData AS tweet
    #                         ON twirp.UserID=tweet.UserID
    #                         GROUP BY twirp.Name
    #                         ORDER BY twirp.Name
    #                         ''')
    #     return [ 
    #                 {
    #                     "name": r[3] ,
    #                     "handle": r[4] , 
    #                     "no_tweets": r[5],
    #                     "newest": r[1],
    #                     'no_collected': r[0], 
    #                     "u_id": r[2]
    #                 } for r in cur.fetchall()
    #             ]


    # def _get_user_data_from_handles(self, handles=[]):
    #     '''Return a dictionary of handles and user_ids for given list of handles.
    #     Return all stored id's if handles is empty list'''
    #     request_sql = '''SELECT UserID, Handle, Name 
    #                         FROM TwirpData
    #                    '''
    #     if handles:
    #         q_marks = ','.join('?'*len(handles))
    #         request_sql += 'WHERE Handle IN (%s)' %q_marks

    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute(request_sql, handles)

    #         return [
    #                     {
    #                         "u_id": r[0],
    #                         "handle": r[1],
    #                         "name":r[2]
    #                     } for r in cur.fetchall()
    #                 ]

    # def _get_user_data_from_identifiers(self, u_ids=[], handles=[], names=[], usernames=[]):
    #     '''Return a dictionary of handles and user_ids for given list of u_ids.
    #     Return all stored id's if u_ids is empty list'''
    #     request_sql = '''SELECT UserID, Handle, Name, UserName, Subscribed 
    #                         FROM TwirpData
    #                    '''
    #     filter_categories = []
    #     filter_args = []
    #     if u_ids:
    #         q_marks = ','.join('?'*len(u_ids))
    #         filter_categories.append('UserID IN (%s)' %q_marks)
    #         filter_args.extend(u_ids)
    #     if names:
    #         q_marks = ','.join('?'*len(names))
    #         filter_categories.append('Name IN (%s)' %q_marks)
    #         filter_args.extend(names)
    #     if handles:
    #         q_marks = ','.join('?'*len(handles))
    #         filter_categories.append('Handle IN (%s)' %q_marks)
    #         filter_args.extend(handles)
    #     if usernames:
    #         q_marks = ','.join('?'*len(usernames))
    #         filter_categories.append('UserName IN (%s)' %q_marks)
    #         filter_args.extend(usernames)

    #     if filter_categories:
    #         request_sql += ' WHERE ' 
    #         request_sql += ' OR '.join(filter_categories)

    #     with sqlite3.connect(self.db_name) as connection:
    #         cur = connection.cursor()
    #         cur.execute(request_sql, filter_args)

    #         return [
    #                     {
    #                         "u_id": r[0],
    #                         "handle": r[1],
    #                         "name":r[2],
    #                         "username": r[3],
    #                         "subscribed":r[4]
    #                     } for r in cur.fetchall()
    #                 ]



    def _delete_twirp(self, u_id, handle, name, username):
        '''Return a dictionary of handles and user_ids for given list of u_ids.
        Return all stored id's if u_ids is empty list'''
        request_sql = '''DELETE FROM TwirpData 
                        WHERE UserID=?
                            AND Handle =?
                            AND Name=?
                            AND UserName=?
                       '''

        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id, handle, name, username))
            cur.execute('SELECT changes() FROM TwirpData')

            return cur.fetchall()[0][0]

    def mark_twirp_subscribed(self, u_id):
        request_sql = '''UPDATE  TwirpData 
                        SET  Subscribed=1
                        WHERE UserID=?
                       '''
        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id,))
            cur.execute('SELECT changes() FROM TwirpData')

            return cur.fetchall()[0][0]


    def mark_twirp_unsubscribed(self, u_id):
        request_sql = '''UPDATE TwirpData 
                        SET  Subscribed=0
                        WHERE UserID=?
                       '''
        with sqlite3.connect(self.db_name) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id,))
            cur.execute('SELECT changes() FROM TwirpData')

            return cur.fetchall()[0][0]


