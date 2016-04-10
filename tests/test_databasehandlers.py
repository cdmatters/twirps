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
                    "subscribed": True,
                    "constituency":"CB"+str(i),
                    "offices":["office"+str(i), "sedge steward"],
            })

        self.node_list[0].properties.update({"username":"MickeyBEyes", "name":"Michael Blue Eyes", "handle":"MBEyes", "favourite_hashtag":"#roth", "party":"DC" })
        self.node_list[1].properties.update({"username":"LittleRichy", "name":"Little Richard", "handle":"LRichy", "favourite_hashtag":"#rawls", "party":"DC" })
        self.node_list[2].properties.update({"username":"TheBoyWonder", "name":"The Boy Wonder", "handle":"tBW", "favourite_hashtag":"#richyfeynman", "party":"Marvel" })
        self.node_list[3].properties.update({"username":"TheKendawg", "name":"Kendog Lamar", "handle":"Kdog", "favourite_hashtag":"#kanye", "party":"Marvel"})
        self.node_list[4].properties.update({"username":"TinyHands", "name":"Tiny Hands", "handle":"tinyhands", "favourite_hashtag":"#ihavetinyhands", "party":"Beano" })

        # Relationships
        # --------------
        # mbe -[MENTION]> lrich
        # mbe -[REPLIES]> ken 
        # lrich -[REPLIES]> mbe
        # tbw -[RETWEETS]> lrich
        # tbw -[MENTIONS_BY_PROXY]> mbe
        # ken -!->
        # th  -!->

        defaults = {
            "mentions":0,
            "mention_last":"",
            "mention_date":"",
            "replies":0,
            "reply_last":"",
            "reply_date":"",
            "retweets":0,
            "retweet_last":"",
            "retweet_date":""
            }

        mbe1 = Relationship(self.node_list[0], "DIRECT" ,self.node_list[1], **defaults)
        mbe2 = Relationship(self.node_list[0], "DIRECT" ,self.node_list[3], **defaults)
        lrich = Relationship(self.node_list[1], "DIRECT", self.node_list[0], **defaults)
        tbw = Relationship(self.node_list[2], "DIRECT", self.node_list[1],  **defaults)
        tbw2 = Relationship(self.node_list[2], "INDIRECT", self.node_list[0],  **defaults)


        mbe1.properties.update({
            "mentions":5,
            "mention_last":"1000000",
            "mention_date":"today"
        })
        mbe2.properties.update({
            "replies":10,
            "reply_last":"2000000",
            "reply_date":"tommorow"
        })
        lrich.properties.update({
            "replies":15,
            "reply_last":"3000000",
            "reply_date":"yesterday"
        })
        tbw.properties.update({
            "retweets":20,
            "retweet_last":"4000000",
            "retweet_date":"thismorning"
        })
        tbw2.properties.update({
            "mentions":1,
            "mention_last":"3000000",
            "mention_date":"yesterday"
        })


        for node in self.node_list:
            self.graph.create(node)
        
        self.graph.create(mbe1)
        self.graph.create(mbe2)
        self.graph.create(lrich)
        self.graph.create(tbw)
        self.graph.create(tbw2)

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
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        test_reference = [
           {
                "name":"Kendog Lamar", 
                "handle":"Kdog", 
                "party":"Marvel",
                "constituency":"CB3",
                "offices":["office3", "sedge steward"],

                "tweets": 30,
                "friends": 150, 
                "followers": 300,
                "archipelago_id": 3,

                "tweeted":[],
                "mentions":[],
                "mention_last":[],
                "mention_date":[],                
                "replies":[],
                "reply_last":[],
                "reply_date":[],
                "retweets":[],
                "retweet_last":[],
                "retweet_date":[],
                "tweet_type":[]

           },
           {
                "name":"The Boy Wonder", 
                "handle":"tBW", 
                "party":"Marvel",
                "constituency":"CB2",
                "offices":["office2", "sedge steward"],

                "tweets": 20,
                "friends": 100, 
                "followers": 200,
                "archipelago_id": 2,

                
                "tweeted":['MBEyes','LRichy'],
                "mentions":[1, 0],
                "mention_last":['3000000', ""],
                "mention_date":['yesterday', ""],                
                "replies":[0,0],
                "reply_last":["",""],
                "reply_date":["",""],
                "retweets":[0, 20],
                "retweet_last":["",'4000000'],
                "retweet_date":["", 'thismorning'],
                "tweet_type":["INDIRECT", "DIRECT"]

           }
        ]

        # Make request
        results = [ _ for _ in neo_db_handler.get_party_nodes('Marvel', 0) ]

        # Test against reference
        self.assertEqual(len(results), 2)
        
        for i in range(2):
            for key in test_reference[i].keys():
                self.assertEqual(results[i][key], test_reference[i][key] )
    
    def test_get_party_nodes_min_tweet(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        test_reference = [
           {
                "name":"Kendog Lamar", 
                "handle":"Kdog", 
                "party":"Marvel",
                "constituency":"CB3",
                "offices":["office3", "sedge steward"],

                "tweets": 30,
                "friends": 150, 
                "followers": 300,
                "archipelago_id": 3,

                "tweeted":[],
                "mentions":[],
                "mention_last":[],
                "mention_date":[],                
                "replies":[],
                "reply_last":[],
                "reply_date":[],
                "retweets":[],
                "retweet_last":[],
                "retweet_date":[],
                "tweet_type":[]
           },
           {
                "name":"The Boy Wonder", 
                "handle":"tBW", 
                "party":"Marvel",
                "constituency":"CB2",
                "offices":["office2", "sedge steward"],

                "tweets": 20,
                "friends": 100, 
                "followers": 200,
                "archipelago_id": 2,

                "tweeted":['LRichy'],
                "mentions":[0],
                "mention_last":[""],
                "mention_date":[""],                
                "replies":[0],
                "reply_last":[""],
                "reply_date":[""],
                "retweets":[20],
                "retweet_last":['4000000'],
                "retweet_date":['thismorning'],
                "tweet_type":["DIRECT"]
           }
        ]

        # Make request
        results = [ _ for _ in neo_db_handler.get_party_nodes('Marvel', 5) ]

        # Test against reference
        self.assertEqual(len(results), 2)

        for i in range(2):
            for key in test_reference[i].keys():
                self.assertEqual(results[i][key], test_reference[i][key] )


    def test_get_cross_party_nodes_default(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        test_reference = [
           {
                "name":"The Boy Wonder", 
                "handle":"tBW", 
                "party":"Marvel",
                "constituency":"CB2",
                "offices":["office2", "sedge steward"],

                "tweets": 20,
                "friends": 100, 
                "followers": 200,
                "archipelago_id": 2,

                "tweeted":['MBEyes','LRichy'],
                "mentions":[1, 0],
                "mention_last":['3000000', ""],
                "mention_date":['yesterday', ""],                
                "replies":[0,0],
                "reply_last":["",""],
                "reply_date":["",""],
                "retweets":[0, 20],
                "retweet_last":["",'4000000'],
                "retweet_date":["", 'thismorning'],
                "tweet_type":["INDIRECT", "DIRECT"]
           }
        ]

        results = [ _ for _ in neo_db_handler.get_cross_party_nodes('Marvel', 'DC', 0 ) ]

        # Test against reference
        self.assertEqual(len(results), 1)

        for i in range(1):
            for key in test_reference[i].keys():
                self.assertEqual(results[i][key], test_reference[i][key] )

    def test_get_cross_party_nodes_min_tweets(self):
        neo_db_handler = NeoDBHandler(n4_database=TEST_GRAPH_DB)

        test_reference = [
           {
                "name":"The Boy Wonder", 
                "handle":"tBW", 
                "party":"Marvel",
                "constituency":"CB2",
                "offices":["office2", "sedge steward"],

                "tweets": 20,
                "friends": 100, 
                "followers": 200,
                "archipelago_id": 2,

                "tweeted":['LRichy'],
                "mentions":[0],
                "mention_last":[""],
                "mention_date":[""],                
                "replies":[0],
                "reply_last":[""],
                "reply_date":[""],
                "retweets":[20],
                "retweet_last":['4000000'],
                "retweet_date":['thismorning'],
                "tweet_type":["DIRECT"]
           }
        ]

        results = [ _ for _ in neo_db_handler.get_cross_party_nodes('Marvel', 'DC', 5) ]

        # Test against reference
        self.assertEqual(len(results), 1)

        for i in range(1):
            for key in test_reference[i].keys():
                self.assertEqual(results[i][key], test_reference[i][key] )



        ########################################################################
        #               ADDING TO DB   (TWIRPS CLASSES)->(PY2NEO OBJS)         #
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
        # TEST: (LRich)->(tinyhands) - mention: ("Hey @tinyhands")
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
        self.assertEqual(relationship.type, u'DIRECT')

        self.assertEqual(relationship["mentions"], 1)
        self.assertEqual(relationship["mention_last"], '1')
        self.assertEqual(relationship["mention_date"], 'a date string')

        self.assertEqual(relationship["replies"], 0)
        self.assertEqual(relationship["reply_last"], '')
        self.assertEqual(relationship["reply_date"], '')
        
        self.assertEqual(relationship["retweets"], 0)
        self.assertEqual(relationship["retweet_last"], '')
        self.assertEqual(relationship["retweet_date"], '')
       

    def test_add_Tweet_to_database__reply(self):
        # TEST: (LRich) ->(tBW) - reply & mention; 
        #       (LRich) ->(tinyhands) mention   EG: (reply->tBW):"Hey @tBW, @tinyhands"
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
        self.assertEqual(results[0][0].type, u'DIRECT')
        self.assertEqual(results[0][1], 'The Boy Wonder')

        self.assertEqual(results[0][0]["mentions"], 0)
        self.assertEqual(results[0][0]["mention_last"], '')
        self.assertEqual(results[0][0]["mention_date"], '')

        self.assertEqual(results[0][0]["replies"], 1)
        self.assertEqual(results[0][0]["reply_last"], '1')
        self.assertEqual(results[0][0]["reply_date"], 'a date string')
        
        self.assertEqual(results[0][0]["retweets"], 0)
        self.assertEqual(results[0][0]["retweet_last"], '')
        self.assertEqual(results[0][0]["retweet_date"], '')


        self.assertEqual(results[1][0].type, u'DIRECT')
        self.assertEqual(results[1][1], 'Tiny Hands')

        self.assertEqual(results[1][0]["mentions"], 1)
        self.assertEqual(results[1][0]["mention_last"], '1')
        self.assertEqual(results[1][0]["mention_date"], 'a date string')

        self.assertEqual(results[1][0]["replies"], 0)
        self.assertEqual(results[1][0]["reply_last"], '')
        self.assertEqual(results[1][0]["reply_date"],  '')
        
        self.assertEqual(results[1][0]["retweets"], 0)
        self.assertEqual(results[1][0]["retweet_last"], '')
        self.assertEqual(results[1][0]["retweet_date"], '')


    def test_add_Tweet_to_database__retweet(self):
        # TEST: (tiny) ->(MBEyes) - reply & mention; 
        #       (tiny) ->(Kdog) mention_by_proxy   EG: (ret->MBE):"Hey @MBE, @Kdog"

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
        self.assertEqual(results[0][0].type, u'INDIRECT')
        self.assertEqual(results[0][1], 'Kendog Lamar')

        self.assertEqual(results[0][0]["mentions"], 1)
        self.assertEqual(results[0][0]["mention_last"], '1')
        self.assertEqual(results[0][0]["mention_date"], 'a date string')

        self.assertEqual(results[0][0]["replies"], 0)
        self.assertEqual(results[0][0]["reply_last"], '')
        self.assertEqual(results[0][0]["reply_date"], '')
        
        self.assertEqual(results[0][0]["retweets"], 0)
        self.assertEqual(results[0][0]["retweet_last"], '')
        self.assertEqual(results[0][0]["retweet_date"], '')


        self.assertEqual(results[1][0].type, u'DIRECT')
        self.assertEqual(results[1][1], 'Michael Blue Eyes')

        self.assertEqual(results[1][0]["mentions"], 0)
        self.assertEqual(results[1][0]["mention_last"], '')
        self.assertEqual(results[1][0]["mention_date"], '')

        self.assertEqual(results[1][0]["replies"], 0)
        self.assertEqual(results[1][0]["reply_last"], '')
        self.assertEqual(results[1][0]["reply_date"], '')
        
        self.assertEqual(results[1][0]["retweets"], 1)
        self.assertEqual(results[1][0]["retweet_last"], '1')
        self.assertEqual(results[1][0]["retweet_date"], 'a date string')



        
        






        
        




        
        







