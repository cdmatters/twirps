import os
import logging
import psycopg2

from neo_dbhandler import NeoDBHandler
from pg_dbhandler import PgDBHandler


LOGGER = logging.getLogger(__name__)

class TDBHandler(object):
    def __init__(self):
        self.neo = NeoDBHandler()
        self.pg = PgDBHandler()

    def create_pg_tables(self):
        self.pg.create_pg_tables()

    def drop_pg_tables(self):
        self.pg.drop_pg_tables()

    def add_Twirp_to_database(self, twirp):
        self.neo.add_Twirp_to_database(twirp)
        self.pg.add_Twirp_to_database(twirp)

    def add_Tweet_to_database(self, tweet):
        self.neo.add_Tweet_to_database(tweet)
        self.pg.add_Tweet_to_database(tweet)

    def get_oldest_tweets_stored_from_mps(self):
        return self.pg.get_oldest_tweets_stored_from_mps()

    def get_newest_tweets_from_mps(self):
        return self.pg.get_newest_tweets_from_mps()

    def get_stored_mps_names(self):
        return self.pg.get_stored_mps_names()
 
    def get_user_data_from_handles(self, handles=[]):
        return self.pg.get_user_data_from_handles(handles)

    def get_user_data_from_identifiers(self, u_ids=[], handles=[], names=[], usernames=[]):
        return self.pg.get_user_data_from_identifiers(u_ids, handles, names, usernames)

    def delete_twirp(self, u_id, handle, name, username):
        return self.pg.delete_twirp(u_id, handle, name, username)

    def mark_twirp_subscribed(self, u_id):
        return self.pg.mark_twirp_subscribed(u_id)

    def mark_twirp_unsubscribed(self, u_id):
        return self.pg.mark_twirp_unsubscribed(u_id)

