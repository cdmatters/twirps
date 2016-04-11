import unittest

from twirps import data_assimilation

class mockObjectFromDict:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

class TestDataAssimilation(unittest.TestCase):
    def test_neo_to_d3map(self):

        test_input =  [
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

        test_reference = [
           {            
                "name": "Kendog Lamar",
                "handle": "Kdog",
                "tweets": 30,
                "friends": 150,
                "followers": 300,
                "party": "Marvel",
                "constituency": "CB3",
                "offices": ["office3", "sedge steward"],
                "o_id": 3,
                "clicked":0,
                "relationships":{
                },                
            },
            {   
                "name": "The Boy Wonder",
                "handle": "tBW",
                "tweets": 20,
                "friends": 100,
                "followers": 200,
                "party": "Marvel",
                "constituency": "CB2",
                "offices": ["office2", "sedge steward"],
                "o_id": 2,
                "clicked":0,
                "relationships":{
                    'LRichy':{'m':None, 'r':None, 't':(20,'4000000'), 'b':None },
                    'MBEyes':{'m':None, 'r':None, 't':None, 'b':(1,'3000000') },
                },
            }
        ]


        mock_object_input = [mockObjectFromDict(**i) for i in test_input]
        results = data_assimilation.neo_to_d3map(mock_object_input)


        self.assertEqual(len(results['nodes']), len(test_reference))
        for i, t in enumerate(test_reference):
            for k in t.keys():
                self.assertEqual(results['nodes'][i][k], test_reference[i][k])

