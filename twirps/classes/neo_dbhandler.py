import os
from py2neo import Graph, Node, schema
from twirp import Twirp

import logging

LOGGER = logging.getLogger(__name__)

class NeoDBHandler(object):
    def __init__(self, n4_database = os.getenv('N4_DATABASE_URL',None)):
        self.n4_database = n4_database


    def test_graph(self):
        n4_graph = Graph(self.n4_database)

    def init_constraints(self):
        n4_graph = Graph(self.n4_database)
        graph_schema = n4_graph.schema
        graph_schema.create_index("Twirp", "handle")
        graph_schema.create_index("Twirp", "user_id")


    def remove_constraints(self):
        n4_graph = Graph(self.n4_database)
        graph_schema = n4_graph.schema
        graph_schema.drop_index("Twirp", "handle")
        graph_schema.drop_index("Twirp", "user_id")


    def add_Twirp_to_database(self, twirp):
        t = twirp
        twirp_node = Node(
            "Twirp",
            twirp.twirps_type_str(),
                user_id=t.id,
                username=t.username,
                name=t.name,
                handle=t.handle,
                followers_count=t.followers_count,
                friends_count=t.friends_count,
                tweet_count=t.tweet_count,
                retweet_count=t.retweet_count,
                been_retweeted_count=t.been_retweet_count,
                favourite_hashtag=t.favourite_hashtag,
                hashtag_count=t.hashtag_count,
                archipelago_id=t.archipelago_id,
                subscribed=t.subscribed
            )

        graph = Graph(self.n4_database)
        graph.create(twirp_node)

    def add_Tweet_to_database(self, tweet):
        pass
