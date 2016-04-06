from twirps.classes  import Twirp, Tweet, TDBHandler, NeoDBHandler, PgDBHandler

import datetime

import unittest
import json
import os

from py2neo import Graph, Node, Relationship

TEST_GRAPH_DB = os.getenv('TEST_N4_DATABASE_URL')

class TestNeoDBHandler(unittest.TestCase):

    def setUp(self):

        self.graph = Graph(TEST_GRAPH_DB)

        self.node_list = [Node("TEST", test_id=i) for i in xrange(5)]
        
        # Nodes
        # -----
        for i, node in enumerate(self.node_list):
            node.labels.add("Twirp")
            node.properties.update({                
                    "user_id": i*100000,
                    "username":"",
                    "name":"",
                    "handle":"",
                    "followers_count":i*100,
                    "friends_count":i*50,
                    "tweet_count":i*10,
                    "retweet_count":i*5,
                    "been_retweeted_count":i*3,
                    "favourite_hashtag":"",
                    "hashtag_count":i*2,
                    "archipelago_id":i*1,
                    "subscribed": True
            })

        self.node_list[0].properties.update({"username":"MickeyBEyes", "name":"Michael Blue Eyes", "handle":"MBEyes", "favourite_hashtag":"#roth" })
        self.node_list[1].properties.update({"username":"LittleRichy", "name":"Little Richard", "handle":"LRichy", "favourite_hashtag":"#rawls" })
        self.node_list[2].properties.update({"username":"TheBoyWonder", "name":"The Boy Wonder", "handle":"tBW", "favourite_hashtag":"#richyfeynman" })
        self.node_list[3].properties.update({"username":"TheKendawg", "name":"Kendog Lamar", "handle":"Kdog", "favourite_hashtag":"#kanye" })
        self.node_list[4].properties.update({"username":"TinyHands", "name":"Tiny Hands", "handle":"tinyhands", "favourite_hashtag":"#ihavetinyhands" })

        # Relationships
        # --------------
        # mbe -[MENTIONS]> lrich
        # mbe -[REPLIES]> ken 
        # lrich -[REPLIES]> mbe
        # tbw  -[RETWEETS]> lrich
        # ken -!->
        # th  -!->

        mbe1 = Relationship(self.node_list[0], "MENTIONS" ,self.node_list[1])
        mbe2 = Relationship(self.node_list[0], "REPLIES" ,self.node_list[3])
        lrich = Relationship(self.node_list[1], "REPLIES", self.node_list[0])
        tbw = Relationship(self.node_list[2], "REPLIES", self.node_list[1])

        mbe1.properties.update({"count":5, "recent":1000000, "date":"today", "url":"this_url"})
        mbe2.properties.update({"count":10, "recent":2000000, "date":"tommorow", "url":"that_url"})
        lrich.properties.update({"count":15, "recent":3000000, "date":"yesterday", "url":"a_url"})
        tbw.properties.update({"count":20, "recent":4000000, "date":"thismorning", "url":"much_url"})

        for node in self.node_list:
            self.graph.create(node)
        
        self.graph.create(mbe1)
        self.graph.create(mbe2)
        self.graph.create(lrich)
        self.graph.create(tbw)

        self.graph.push()

    def tearDown(self):
        
        # remove test items
        self.graph.cypher.execute("MATCH (n:TEST) DETACH DELETE n")

        empty_list = [ _ for _ in self.graph.find('TEST') ]
        self.assertEqual( empty_list, [])




        ########################################################################
        #                          CYPHER QUERIES                              #
        ########################################################################

    def test_get_party_nodes(self):
        pass

    def test_get_cross_party_nodes(self):
        pass



        ########################################################################
        #                          ADDING TO DB                                #
        ########################################################################
        
    def test_add_Twirp_to_database(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        # Test Data
        new_twirp = Twirp(None, 'test')
        new_twirp.id = 314150000000
        new_twirp.username = 'BilboBagginsMP'
        new_twirp.name = 'Bilbo Baggins'
        new_twirp.handle = 'bilbo'
        new_twirp.followers_count = 20
        new_twirp.friends_count = 30
        new_twirp.tweet_count = 40
        new_twirp.retweet_count = 50
        new_twirp.been_retweet_count = 60 
        new_twirp.favourite_hashtag = '#onering'
        new_twirp.hashtag_count = 70
        new_twirp.archipelago_id = 80 
        new_twirp.twirps_type = -1
        new_twirp.subscribed = False
        new_twirp.geo = False

        # Add to database (with 'TEST' label)
        neo_db_handler.add_Twirp_to_database(new_twirp, is_test_mode=True)

        # Check results
        results = [ _ for _ in self.graph.cypher.execute(
                                    "MATCH (n {handle:'bilbo'}) RETURN n")]        
        self.assertEqual(len(results), 1)
        node = results[0][0]

        # Interrogate Node
        self.assertEqual(node.get_labels(), [u'TEST', u'Twirp', u'Other'])

        self.assertEqual(node["user_id"],314150000000)
        self.assertEqual(node["username"],'BilboBagginsMP')
        self.assertEqual(node["name"],'Bilbo Baggins')
        self.assertEqual(node["handle"],'bilbo')
        self.assertEqual(node["followers_count"],20)
        self.assertEqual(node["friends_count"],30)
        self.assertEqual(node["tweet_count"],40)
        self.assertEqual(node["retweet_count"],50)
        self.assertEqual(node["been_retweeted_count"],60 )
        self.assertEqual(node["favourite_hashtag"],'#onering')
        self.assertEqual(node["hashtag_count"],70)
        self.assertEqual(node["archipelago_id"],80 )
        self.assertEqual(node["subscribed"],False)


    def test_add_Tweet_to_database__mention(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        # Test Data
        new_tweet = Tweet(None, 'test')

        new_tweet.tweet_id = 1
        new_tweet.user_id = 100000
        new_tweet.handle = 'LRichy'
        new_tweet.mentions = [(400000, 'tinyhands')] 
        new_tweet.content = 'Generic tweet @tinyhands'  # not stored here
        
        new_tweet.is_retweet = False
        new_tweet.retweeted_user = None
        new_tweet.retweet_status_id = 0
        
        new_tweet.is_reply = False
        new_tweet.in_reply_to_user = None
        new_tweet.in_reply_to_status_id = None
        
        new_tweet.retweet_count = 3           # not stored here
        new_tweet.favourite_count = 4         # not stored here
        new_tweet.hashtags = ['clothes']      # not stored here
        new_tweet.date = 'a date string'
        new_tweet.urls = ['https://url.com']  # not stored here
        new_tweet.website_link = 'twitter.com/status/madeupstatus1'

        # Add to database
        neo_db_handler.add_Tweet_to_database(new_tweet)

        # Preliminary check 
        results = [ _ for _ in self.graph.cypher.execute(
                    """MATCH (a {handle:'LRichy'})-[r]->(b {handle:'tinyhands'})
                       RETURN r""")]        
        self.assertEqual(len(results), 1)
        relationship =  results[0][0]

        # In depth check
        self.assertEqual(relationship.type, u'MENTION')

        self.assertEqual(relationship["count"], 1)
        self.assertEqual(relationship["recent"],'1')
        self.assertEqual(relationship["date"],'a date string')
        self.assertEqual(relationship["url"],"twitter.com/status/madeupstatus1")

    def test_add_Tweet_to_database__reply(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        # Test Data
        new_tweet = Tweet(None, 'test')

        new_tweet.tweet_id = 1
        new_tweet.user_id = 100000
        new_tweet.handle = 'LRichy'
        new_tweet.mentions = [(400000, 'tinyhands'), (200000, 'tBW')] 
        new_tweet.content = 'Generic tweet @tinyhands @tBW'  # not stored here      
        
        new_tweet.is_retweet = False
        new_tweet.retweeted_user = None
        new_tweet.retweet_status_id = 0
        
        new_tweet.is_reply = True
        new_tweet.in_reply_to_user = (200000, 'tBW')
        new_tweet.in_reply_to_status_id = 2
        
        new_tweet.retweet_count = 3              # not stored here   
        new_tweet.favourite_count = 4            # not stored here
        new_tweet.hashtags = ['clothes']         # not stored here
        new_tweet.date = 'a date string'
        new_tweet.urls = ['https://url.com/']    # not stored here
        new_tweet.website_link = 'twitter.com/status/madeupstatus1'

        # Add to database
        neo_db_handler.add_Tweet_to_database(new_tweet) 

        # Preliminary check
        results = [ _ for _ in self.graph.cypher.execute(
                                """MATCH (a {handle:'LRichy'})-[r]->(b) 
                                   WHERE b.handle<>'MBEyes' 
                                   RETURN r, b.name ORDER BY b.name""")]        
        
        self.assertEqual(len(results), 2)

        # In depth check
        self.assertEqual(results[0][0].type, u'REPLY')
        self.assertEqual(results[0][1], 'The Boy Wonder')

        self.assertEqual(results[0][0]["count"], 1)
        self.assertEqual(results[0][0]["recent"],'2')  # replied tweet no
        self.assertEqual(results[0][0]["date"],'a date string')
        self.assertEqual(results[0][0]["url"],"twitter.com/status/madeupstatus1")

        self.assertEqual(results[1][0].type, u'MENTION')
        self.assertEqual(results[1][1], 'Tiny Hands')

        self.assertEqual(results[1][0]["count"], 1)
        self.assertEqual(results[1][0]["recent"],'1')
        self.assertEqual(results[1][0]["date"],'a date string')
        self.assertEqual(results[1][0]["url"],"twitter.com/status/madeupstatus1")


    def test_add_Tweet_to_database__retweet(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        # Test Data
        new_tweet = Tweet(None, 'test')

        new_tweet.tweet_id = 1
        new_tweet.user_id = 400000
        new_tweet.handle = 'tinyhands'
        new_tweet.mentions = [(300000, 'Kdog')] 
        new_tweet.content = 'Generic tweet @Kdog'  # not stored here

        new_tweet.is_retweet = True
        new_tweet.retweeted_user = (0, 'MBEyes')
        new_tweet.retweet_status_id = 2

        new_tweet.is_reply = False
        new_tweet.in_reply_to_user = None
        new_tweet.in_reply_to_status_id = None
        
        new_tweet.retweet_count = 3                # not stored here
        new_tweet.favourite_count = 4              # not stored here
        new_tweet.hashtags = []                    # not stored here
        new_tweet.date = 'a date string'
        new_tweet.urls = ['https://url.com/']      # not stored here
        new_tweet.website_link = 'twitter.com/status/madeupstatus1'

        # Add to database
        neo_db_handler.add_Tweet_to_database(new_tweet) 

        # Preliminary check
        results = [ _ for _ in self.graph.cypher.execute(
                                    """MATCH (a {handle:'tinyhands'})-[r]->(b) 
                                    RETURN r, b.name ORDER BY b.name""")]        

        self.assertEqual(len(results), 2)

        # In depth check
        self.assertEqual(results[0][0].type, u'MENTION_BY_PROXY')
        self.assertEqual(results[0][1], 'Kendog Lamar')

        self.assertEqual(results[0][0]["count"], 1)
        self.assertEqual(results[0][0]["recent"],'2')  # the retweet
        self.assertEqual(results[0][0]["date"],'a date string')
        self.assertEqual(results[0][0]["url"],"twitter.com/status/madeupstatus1")

        self.assertEqual(results[1][0].type, u'RETWEET')
        self.assertEqual(results[1][1], 'Michael Blue Eyes')

        self.assertEqual(results[1][0]["count"], 1)
        self.assertEqual(results[1][0]["recent"],'2')
        self.assertEqual(results[1][0]["date"],'a date string')
        self.assertEqual(results[1][0]["url"],"twitter.com/status/madeupstatus1")






        
        






        
        




        
        







