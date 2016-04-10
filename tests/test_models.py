from twirps.classes  import Tweet

from twirps.data_collection import authorize_twitter

import datetime

import unittest
import json
import os

class TestTweetModel(unittest.TestCase):
    def setUp(self):
        self.api = authorize_twitter()


    def tearDown(self):
        pass

    def test_parse_mention(self):
        # https://twitter.com/condnsdmatters/status/715174694958272513
        # Tweet: 715174694958272513 condnsdmatters || RC: 0 || FC: 0 || RT: None || @ 1 || # 0 || Url 0
        # Content: platy loves @GOVUK
        status = self.api.get_status(715174694958272513)
        test_tweet = Tweet(status, 'twitter')

        self.assertEqual(test_tweet.tweet_id, 715174694958272513)
        self.assertEqual(test_tweet.user_id, 701110092675031041)
        self.assertEqual(test_tweet.handle, 'condnsdmatters')
        self.assertEqual(test_tweet.mentions, [(17481977, 'GOVUK')]) 
        self.assertEqual(test_tweet.content,  'platy loves @GOVUK')
        self.assertEqual(test_tweet.is_retweet, False  )
        self.assertEqual(test_tweet.retweeted_user, None)
        self.assertEqual(test_tweet.retweet_count, 0)
        self.assertEqual(test_tweet.favourite_count, 0)
        self.assertEqual(test_tweet.hashtags, [])
        self.assertEqual(test_tweet.date, datetime.datetime(2016, 3, 30, 13, 51, 49) )
        self.assertEqual(test_tweet.urls,  [])
        self.assertEqual(test_tweet.in_reply_to_status_id, None)
        self.assertEqual(test_tweet.in_reply_to_user, None)
        self.assertEqual(test_tweet.is_reply, False  )
    
    def test_parse_mention_hash_link(self):
        # https://twitter.com/GOVUK/status/673864586982854657
        # Tweet: 673864586982854657 GOVUK || RC: 17 || FC: 9 || RT: None || @ 1 || # 1 || Url 1
        # Content: For the latest on the floods, please follow @EnvAgency, #floodaware or visit GOV.UK: https://t.co/kZAdl7JvKb
        status = self.api.get_status(673864586982854657)
        test_tweet = Tweet(status, 'twitter')
      
        self.assertEqual(test_tweet.tweet_id, 673864586982854657)
        self.assertEqual(test_tweet.user_id, 17481977)
        self.assertEqual(test_tweet.handle, 'GOVUK')
        self.assertEqual(test_tweet.mentions, [(47331384, 'EnvAgency')]) 
        self.assertEqual(test_tweet.content,  'For the latest on the floods, please follow @EnvAgency, #floodaware or visit GOV.UK: https://t.co/kZAdl7JvKb')
        self.assertEqual(test_tweet.is_retweet, False  )
        self.assertEqual(test_tweet.retweeted_user, None)
        self.assertEqual(test_tweet.retweet_count, 17)
        self.assertEqual(test_tweet.favourite_count, 9)
        self.assertEqual(test_tweet.hashtags, ['floodaware'])
        self.assertEqual(test_tweet.date, datetime.datetime(2015, 12, 7, 14, 0, 11) )
        self.assertEqual(test_tweet.urls,  ['https://www.gov.uk/prepare-for-a-flood/find-out-if-youre-at-risk'])
        self.assertEqual(test_tweet.in_reply_to_status_id, None)
        self.assertEqual(test_tweet.in_reply_to_user, None)
        self.assertEqual(test_tweet.is_reply, False  )

    def test_parse_retweet(self):
        # https://twitter.com/condnsdmatters/status/715175357658374148
        # Tweet: 715175357658374148 condnsdmatters || RC: 17 || FC: 0 || RT: GOVUK || @ 1 || # 1 || Url 1
        # Content: For the latest on the floods, please follow @EnvAgency, #floodaware or visit GOV.UK: https://t.co/kZAdl7JvKb
        status = self.api.get_status(715175357658374148)
        test_tweet = Tweet(status, 'twitter')

        self.assertEqual(test_tweet.tweet_id, 715175357658374148)
        self.assertEqual(test_tweet.user_id, 701110092675031041)
        self.assertEqual(test_tweet.handle, 'condnsdmatters')
        self.assertEqual(test_tweet.mentions, [(47331384, 'EnvAgency')]) 
        self.assertEqual(test_tweet.content,  'For the latest on the floods, please follow @EnvAgency, #floodaware or visit GOV.UK: https://t.co/kZAdl7JvKb')
        self.assertEqual(test_tweet.is_retweet, True  )
        self.assertEqual(test_tweet.retweet_status_id, 673864586982854657)
        self.assertEqual(test_tweet.retweeted_user, (17481977, 'GOVUK'))
        self.assertEqual(test_tweet.retweet_count, 17)
        self.assertEqual(test_tweet.favourite_count, 0)
        self.assertEqual(test_tweet.hashtags, ['floodaware'])
        self.assertEqual(test_tweet.date, datetime.datetime(2016, 3, 30, 13, 54, 27) )
        self.assertEqual(test_tweet.urls,  ['https://www.gov.uk/prepare-for-a-flood/find-out-if-youre-at-risk'])
        self.assertEqual(test_tweet.in_reply_to_status_id, None)
        self.assertEqual(test_tweet.in_reply_to_user, None)
        self.assertEqual(test_tweet.is_reply, False  )

    def test_parse_reply_on_other(self):
        # https://twitter.com/WhittakerTrevor/status/674157223334060032
        # Tweet: 674157223334060032 WhittakerTrevor || RC: 0 || FC: 0 || RT: REPLY || @ 2 || # 0 || Url 0
        # Content: @GOVUK @EnvAgency STOP CUTTING GREEN SUBSIDIES WHAT YOU TRYING TO SAVE MONEY FOR MONEY YOU WONT NEED IT WHEN YOU HAVE DESYROYED THE EARTH
        status = self.api.get_status(674157223334060032)
        test_tweet = Tweet(status, 'twitter')

        self.assertEqual(test_tweet.tweet_id, 674157223334060032)
        self.assertEqual(test_tweet.user_id, 464109437)
        self.assertEqual(test_tweet.handle, 'WhittakerTrevor')
        self.assertEqual(test_tweet.mentions, [(17481977, 'GOVUK'), (47331384, 'EnvAgency')]) 
        self.assertEqual(test_tweet.content,  '@GOVUK @EnvAgency STOP CUTTING GREEN SUBSIDIES WHAT YOU TRYING TO SAVE MONEY FOR MONEY YOU WONT NEED IT WHEN YOU HAVE DESYROYED THE EARTH')
        self.assertEqual(test_tweet.is_retweet, False  )
        self.assertEqual(test_tweet.retweet_status_id, 0)
        self.assertEqual(test_tweet.retweeted_user, None)
        self.assertEqual(test_tweet.retweet_count, 0)
        self.assertEqual(test_tweet.favourite_count, 0)
        self.assertEqual(test_tweet.hashtags, [])
        self.assertEqual(test_tweet.date, datetime.datetime(2015, 12, 8, 9, 23, 1) )
        self.assertEqual(test_tweet.urls,  [])
        self.assertEqual(test_tweet.in_reply_to_status_id, 673864586982854657)
        self.assertEqual(test_tweet.in_reply_to_user, (17481977, 'GOVUK'))
        self.assertEqual(test_tweet.is_reply, True  )
 
    def test_parse_reply_on_self(self):
       # https://twitter.com/annaturley/status/714936442384990208
       # Tweet: 714936442384990208 annaturley || RC: 2 || FC: 0 || RT: REPLY || @ 1 || # 0 || Url 0
       # Content: @Opensout I want them to step in and take control of the site. I am just gutted they wouldn't consider this for Redcar.
        status = self.api.get_status(714936442384990208)
        test_tweet = Tweet(status, 'twitter')

        self.assertEqual(test_tweet.tweet_id, 714936442384990208)
        self.assertEqual(test_tweet.user_id, 22398060)
        self.assertEqual(test_tweet.handle, 'annaturley')
        self.assertEqual(test_tweet.mentions, [(3002057294, u'Opensout')]) 
        self.assertEqual(test_tweet.content,  "@Opensout I want them to step in and take control of the site. I am just gutted they wouldn't consider this for Redcar.")
        self.assertEqual(test_tweet.is_retweet, False  )
        self.assertEqual(test_tweet.retweet_status_id, 0)
        self.assertEqual(test_tweet.retweeted_user, None)
        self.assertEqual(test_tweet.retweet_count, 2)
        self.assertEqual(test_tweet.favourite_count, 0)
        self.assertEqual(test_tweet.hashtags, [])
        self.assertEqual(test_tweet.date, datetime.datetime(2016, 3, 29, 22, 5, 5) )
        self.assertEqual(test_tweet.urls,  [])
        self.assertEqual(test_tweet.in_reply_to_status_id, 714935890695614466)
        self.assertEqual(test_tweet.in_reply_to_user, (3002057294, u'Opensout'))
        self.assertEqual(test_tweet.is_reply, True  )

    # def test_user_timeline(self):
    #     tweets = self.api.user_timeline()
    #     print
    #     for t in tweets:
    #         print Tweet(t, 'twitter')
 
if __name__=='__main__':
    unittest.main(verbosity=2)


    def test_return_constituency_list(self):
        '''ACCESS:: Test all constituencies returned in a list''' 
        arch = archipelago.Archipelago("sqlite:///test.db")
        constituency_list = arch.get_constituencies()

        start_constituencies = [u'Aberavon', u'Aberconwy', u'Aberdeen North']
        end_constituencies =  [u'Ynys M\xf4n', u'York Central', u'York Outer']
 
        # Test correct 
        self.assertEqual(len(constituency_list), 650 )
        self.assertEqual( start_constituencies, constituency_list[:3] )
        self.assertEqual( end_constituencies, constituency_list[-3:] )

