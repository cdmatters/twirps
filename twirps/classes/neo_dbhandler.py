# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
from py2neo import Graph, Node, schema, batch


import logging

LOGGER = logging.getLogger(__name__)

class NeoDBHandler(object):
    def __init__(self, n4_database = os.getenv('N4_DATABASE_URL', None) ):
        self.n4_database = n4_database

        self.map_format_return = u"""
                   a.name AS name, 
                   a.handle AS handle,
                   a.party AS party,
                   a.constituency AS constituency,
                   a.offices AS offices,
                   a.tweet_count AS tweets,
                   a.friends_count AS friends, 
                   a.followers_count AS followers,
                   a.archipelago_id AS archipelago_id,
                    collect(b.handle) as tweeted, 
                    collect(r.mentions) as mentions,
                    collect(r.mention_last) as mention_last,
                    collect(r.mention_date) as mention_date,
                    collect(r.replies) as replies,
                    collect(r.reply_last) as reply_last,
                    collect(r.reply_date) as reply_date,
                    collect(r.retweets) as retweets,
                    collect(r.retweet_last) as retweet_last,
                    collect(r.retweet_date) as retweet_date,
                    collect(type(r)) as tweet_type
                """

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

        if not tweet.mentions and not tweet.is_reply and not tweet.is_retweet:
            # dont waste my time: quick return
            return
        
        # In the pg database we store tweets as is, straight from twitter
        # EG @A -[reply]->B: content - "Hey @B, how are you"
        # This gives a reply AND a mention (since you can reply without mentioning)
        
        # The neo db now needs to filter duplicates 
        def _is_not_double_counted(mention):
            if tweet.is_reply:
                return mention[0] != tweet.in_reply_to_user[0]
            if tweet.is_retweet:
                return mention[0] != tweet.retweeted_user[0]
            else:
                return True

        tweet.mentions = filter(_is_not_double_counted, tweet.mentions)


        # Build custom cypher request for input type
        def _build_cypher(request_type):
            request_array = ['']*8
            
            request_array[0] = u'''
                MATCH (a:Twirp { user_id: {twirp} }), (b:Twirp { user_id: {tweeted} })
                MERGE (a)-[r:«type» {archive:0}]->(b)
                ON CREATE SET '''
            request_array[1]=u'''
                    r.mentions = {m},
                    r.mention_last = {m_l},
                    r.mention_date = {m_d}, '''
            request_array[2]=u'''
                    r.replies = {r},
                    r.reply_last = {r_l},
                    r.reply_date = {r_d}, '''
            request_array[3]=u'''
                    r.retweets = {t},
                    r.retweet_last = {t_l},
                    r.retweet_date = {t_d} '''
            request_array[4]=u'''
                ON MATCH SET '''
            request_array[5]=u'''
                    r.mentions = r.mentions + {m},
                    r.mention_last = {m_l},
                    r.mention_date = {m_d} '''
            request_array[6]=u'''
                    r.replies = r.replies + {r},
                    r.reply_last = {r_l},
                    r.reply_date = {r_d} '''
            request_array[7]=u'''
                    r.retweets = r.retweets + {t},
                    r.retweet_last = {t_l},
                    r.retweet_date = {t_d}
            '''

            if request_type!='m':
                request_array[5] = ''
                request_array[1] = request_array[1].format(m=0,m_l='""',m_d='""')
            if request_type!='r':
                request_array[6] = ''
                request_array[2] = request_array[2].format(r=0,r_l='""',r_d='""')
            if request_type!='t':
                request_array[7] = ''
                request_array[3] = request_array[3].format(t=0,t_l='""',t_d='""')
            return ''.join(request_array)



        # default_params {
        #     'm':0, 'm_d':'', 'm_l':'',
        #     'r':0, 'r_d':'', 'r_d':'',
        #     't':0, 't_d':''}

        requests = []

        mentions_request_input = [
            (   _build_cypher('m'),
                { 
                    "twirp" : tweet.user_id,
                    "tweeted": mentioned[0],
                    "type": "DIRECT" if not tweet.is_retweet else "INDIRECT",
                    "m":1,
                    "m_d":tweet.date,
                    "m_l": str(tweet.tweet_id)
                }
            ) for mentioned in tweet.mentions ]

        replies_request_input = [
            ( _build_cypher('r'),
                { 
                    "twirp" : tweet.user_id,
                    "tweeted": tweet.in_reply_to_user[0],
                    "type": "DIRECT",
                    "r":1,
                    "r_d": tweet.date,
                    "r_l": str(tweet.tweet_id)
                }
            )] if tweet.is_reply else []

        retweets_request_input = [
            ( _build_cypher('t'),
                { 
                    "twirp" : tweet.user_id,
                    "tweeted": tweet.retweeted_user[0],
                    "type": "DIRECT",
                    "t":1,
                    "t_d": tweet.date,
                    "t_l": str(tweet.tweet_id)
                }
            )] if tweet.is_retweet else []


        requests.extend(mentions_request_input)
        requests.extend(replies_request_input)
        requests.extend(retweets_request_input)


        graph = Graph(self.n4_database)
        
        transfer = graph.cypher.begin()
        for req in requests:
            transfer.append(req[0], req[1])
        transfer.commit()

    def get_full_map(self, min_tweets):
        cypher_request = u''' 
            MATCH (a)
            OPTIONAL MATCH (a)-[r]->(b) 
            WHERE r.mentions + r.retweets + r.replies >= {min_tweets} 
                AND a <> b
            RETURN ''' + self.map_format_return

        request_input = {'min_tweets':min_tweets}

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request, request_input)

    def get_party_nodes(self, partyA, min_tweets):
        cypher_request = u''' 
            MATCH (a {party:{node_partyA}})
            OPTIONAL MATCH (a)-[r]->(b)
            WHERE a.party = {node_partyA}
                AND r.mentions + r.retweets + r.replies >= {min_tweets} 
                AND a <> b
            RETURN ''' + self.map_format_return

        request_input = {'node_partyA':partyA, 'min_tweets':min_tweets}

        graph = Graph(self.n4_database)
        return graph.cypher.execute(cypher_request, request_input)

    def get_cross_party_nodes(self, partyA, partyB, min_tweets):
        cypher_request = u''' 
            MATCH (a)-[r]->(b)
            WHERE a.party = {node_partyA}
                AND b.party = {node_partyB}  
                AND a <> b
                AND r.mentions + r.retweets + r.replies >= {min_tweets} 
            RETURN ''' + self.map_format_return

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

