# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
from py2neo import Graph, Node, schema, batch


import logging

LOGGER = logging.getLogger(__name__)

class NeoDBHandler(object):
    def __init__(self, n4_database = os.getenv('N4_DATABASE_URL', None) ):
        self.n4_database = n4_database

    def test_graph(self):
        n4_graph = Graph(self.n4_database)

    def init_constraints(self):
        n4_graph = Graph(self.n4_database)
        graph_schema = n4_graph.schema
        graph_schema.create_index("Twirp", "handle")
        graph_schema.create_index("Twirp", "user_id")
        LOGGER.debug("Init' constraints, name at: %s" % self.n4_database )

    def remove_constraints(self):
        n4_graph = Graph(self.n4_database)
        graph_schema = n4_graph.schema
        graph_schema.drop_index("Twirp", "handle")
        graph_schema.drop_index("Twirp", "user_id")
        LOGGER.debug("Deleted all indices at: %s" % self.n4_database )

    def add_Twirp_to_database(self, twirp, is_test_mode=False):
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

        if is_test_mode:
            twirp_node.labels.add("TEST")

        graph = Graph(self.n4_database)
        graph.create(twirp_node)

    def add_Tweet_to_database(self, tweet):
        if not tweet.mentions:
            return
        cypher_request = u'''
            MATCH (a:Twirp { user_id: {twirp} }), (b:Twirp { user_id: {tweeted} })
            MERGE (a)-[r:«type» {archive:0}]->(b)
            ON CREATE SET
                r.count = 1,
                r.recent={tweet_id},
                r.date={date},
                r.url={url}
            ON MATCH SET
                r.count = r.count + 1,
                r.recent = {tweet_id},
                r.date={date},
                r.url={url}
        ''' 

        requests = []
        
        _proxy="_BY_PROXY" if tweet.is_retweet else ""
        mention_tweet_id = tweet.tweet_id if not tweet.is_retweet else tweet.retweet_status_id

        mentions_request_input = [{ 
            "twirp" : tweet.user_id,
            "tweeted": mentioned[0],
            "type": "MENTION"+_proxy,
            "tweet_id": str(mention_tweet_id),
            "date":tweet.date,
            "url": tweet.website_link
            } for mentioned in tweet.mentions if not tweet.is_reply or mentioned[0]!=tweet.in_reply_to_user[0]]
        requests.extend(mentions_request_input)

        retweet_request_input = [{ 
            "twirp" : tweet.user_id,
            "tweeted": tweet.retweeted_user[0],
            "type": "RETWEET",
            "tweet_id": str(tweet.retweet_status_id),
            "date":tweet.date,
            "url": tweet.website_link
            }] if tweet.is_retweet else []
        requests.extend(retweet_request_input)

        reply_request_input = [{ 
            "twirp" : tweet.user_id,
            "tweeted": tweet.in_reply_to_user[0],
            "type": "REPLY",
            "tweet_id": str(tweet.in_reply_to_status_id),
            "date":tweet.date,
            "url": tweet.website_link
            }] if tweet.is_reply else []
        requests.extend(reply_request_input)


        graph = Graph(self.n4_database)
        
        transfer = graph.cypher.begin()
        for req in requests:
            transfer.append(cypher_request, req)
        transfer.commit()

    def get_full_map(self, min_tweets):
        cypher_request = u''' 
            MATCH (a)
            OPTIONAL MATCH (a)-[r]->(b) 
            WHERE r.count >= {min_tweets} 
                AND a <> b
            RETURN a.name AS name, 
                   a.handle AS handle,
                   a.party AS party,
                   a.constituency AS constituency,
                   a.offices AS offices,
                   a.tweet_count AS tweets,
                   a.friends_count AS friends, 
                   a.followers_count AS followers,
                   a.archipelago_id AS archipelago_id,
                    collect(b.handle) as tweeted, 
                    collect(r.count) as count,
                    collect(type(r)) as tweet_type,
                    collect(r.url) as recent_url,
                    collect(r.recent) as recent
        '''

        request_input = {'min_tweets':min_tweets}

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request, request_input)

    def get_party_nodes(self, partyA, min_tweets):
        cypher_request = u''' 
            MATCH (a {party:{node_partyA}})
            OPTIONAL MATCH (a)-[r]->(b)
            WHERE a.party = {node_partyA}
                AND r.count >= {min_tweets} 
                AND a <> b
            RETURN a.name AS name, 
                   a.handle AS handle,
                   a.party AS party,
                   a.constituency AS constituency,
                   a.offices AS offices,
                   a.tweet_count AS tweets,
                   a.friends_count AS friends, 
                   a.followers_count AS followers,
                   a.archipelago_id AS archipelago_id,
                    collect(b.handle) as tweeted, 
                    collect(r.count) as count,
                    collect(type(r)) as tweet_type,
                    collect(r.url) as recent_url,
                    collect(r.recent) as recent
                '''

        request_input = {'node_partyA':partyA, 'min_tweets':min_tweets}

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request, request_input)

    def get_cross_party_nodes(self, partyA, partyB, min_tweets):
        cypher_request = u''' 
            MATCH (a)-[r]->(b)
            WHERE a.party = {node_partyA}
                AND b.party = {node_partyB}  
                AND a <> b
                AND r.count >= {min_tweets} 
            RETURN a.name AS name, 
                   a.handle AS handle,
                   a.party AS party,
                   a.constituency AS constituency,
                   a.offices AS offices,
                   a.tweet_count AS tweets,
                   a.friends_count AS friends, 
                   a.followers_count AS followers,
                   a.archipelago_id AS archipelago_id,
                    collect(b.handle) as tweeted, 
                    collect(r.count) as count,
                    collect(type(r)) as tweet_type,
                    collect(r.url) as recent_url,
                    collect(r.recent) as recent
                '''

        request_input = {'node_partyA':partyA, 'node_partyB':partyB, 'min_tweets':min_tweets}

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request, request_input)

    def delete_graph_data(self):
        cypher_request = u''' 
            MATCH (n) DETACH DELETE n
        '''

        graph = Graph(self.n4_database)
        LOGGER.debug("Deleted all data at: %s" % self.n4_database )
        return graph.cypher.execute(cypher_request)

    def update_with_arch_mp_list(self, mp_list):
        graph = Graph(self.n4_database)

        node_batch =  batch.PushBatch(graph)
        for mp in mp_list:
            mp_node = graph.find_one('Twirp', 'archipelago_id', mp.OfficialId)
            if mp_node:
                mp_node.properties["party"] = unicode(mp.Party) if mp.Party!='Labour/Co-operative' else 'Labour'
                mp_node.properties["twirp_type"] = 1
                mp_node.properties["constituency"] = unicode(mp.Constituency)
                mp_node.properties["offices"] = [ office.Office for office in mp.Offices] if mp.Offices else ['']
             
                node_batch.append(mp_node)

        node_batch.push()


    def archive_map(self):
        r_types = ['MENTION', 'RETWEET', 'REPLY', 'MENTION_BY_PROXY']
        cypher_request = u'''
            MATCH ()-[r:«label»]-()
            SET r.archive = 1
        '''
        graph = Graph(self.n4_database)
        for i in r_types:
            graph.cypher.execute(cypher_request, {u'label':i,u'labelA':i, u'_label':'_'+i})

    def delete_archived_map(self):
        cypher_request = u'''
            MATCH ()-[r {archive:1}]-()
            DELETE r
        '''
        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request)

    def unarchive_map(self):
        LOGGER.info('Replacing map with archive')
        cypher_request1 = u'''
            MATCH ()-[r {archive:0}]-()
            DELETE r
        '''
        cypher_request2 = u'''
            MATCH ()-[r {archive:1}]-()
            SET r.archive = 0
        '''
        graph = Graph(self.n4_database)
        graph.cypher.execute(cypher_request1)
        graph.cypher.execute(cypher_request2)

