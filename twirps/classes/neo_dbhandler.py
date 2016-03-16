# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
from py2neo import Graph, Node, schema


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
        if not tweet.mentions:
            return
        cypher_request = u'''
            MATCH (a:Twirp { user_id: {twirp} }), (b:Twirp { user_id: {tweeted} })
            MERGE (a)-[r:«type»]->(b)
            ON CREATE SET
                r.count = 1,
                r.recent={tweet_id},
                r.date={date}
            ON MATCH SET
                r.count = r.count + 1,
                r.recent = {tweet_id},
                r.date={date}
        ''' 

        requests = []
        
        mentions_request_input = [{ 
            "twirp" : tweet.userid,
            "tweeted": mentioned[0],
            "type": "REPLY",
            "tweet_id": tweet.tweetid,
            "date":tweet.date
            } for mentioned in tweet.mentions if mentioned[1]!=tweet.retweet]
        requests.extend(mentions_request_input)

        retweet_request_input = [{ 
            "twirp" : tweet.userid,
            "tweeted": tweet.mentions[-1][0],
            "type": "RETWEET",
            "tweet_id": tweet.retweeted_uid,
            "date":tweet.date
            }] if tweet.retweeted_uid else []
        requests.extend(retweet_request_input)

        graph = Graph(self.n4_database)
        
        transfer = graph.cypher.begin()
        for req in requests:
            transfer.append(cypher_request, req)
        transfer.commit()

    def get_all_nodes(self):
        cypher_request = u''' 
            MATCH (a)-[r]->(b) 
            WHERE r.count > 1
            RETURN a.name AS name, collect(b.name) as tweeted, collect(r.count) as count, collect(r.type) as type
        '''

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request)

    def delete_graph_data(self):
        cypher_request = u''' 
            MATCH (n) DETACH DELETE n
        '''

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request)


