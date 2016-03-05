import sqlite3
import os
import logging
import psycopg2


LOGGER = logging.getLogger(__name__)

class TDBHandler(object):
    def __init__(self, pg_database = os.getenv('PG_DATABASE_URL',None)):
        self.pg_database = pg_database

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

        T = tweet
        input_tuple = (T.tweetid,
                       T.userid, T.handle,
                       T.retweet,
                       T.content,   
                       T.favourite_count, T.retweet_count,
                       T.date)

        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(add_tweet_sql, input_tuple)
            for h in T.hashtags:
                cur.execute(add_entity_sql, (T.tweetid, T.userid, 'hashtag', h, 0))
            for u in T.urls:
                cur.execute(add_entity_sql, (T.tweetid, T.userid, 'url', u, 0))
            for m in T.mentions:
                cur.execute(add_entity_sql, (T.tweetid, T.userid, 'mention', m[1], m[0]))

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
    
    def mark_twirp_subscribed(self, u_id):
        request_sql = '''UPDATE  TwirpData 
                        SET  Subscribed=TRUE
                        WHERE UserID=%s
                       '''
        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id,))

            return cur.rowcount


    def mark_twirp_unsubscribed(self, u_id):
        request_sql = '''UPDATE TwirpData 
                        SET  Subscribed=FALSE
                        WHERE UserID=%s
                       '''
        with psycopg2.connect(self.pg_database) as connection:
            cur = connection.cursor()
            cur.execute(request_sql, (u_id,))

            return cur.rowcount
