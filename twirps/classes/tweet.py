import logging

LOGGER = logging.getLogger(__name__)


class Tweet(object):
    def __init__(self, tweet, source):
        self.tweet_id = 0
        self.user_id = 0
        self.handle = ''
        self.mentions = [] 
        self.content = ''
        self.is_retweet = False
        self.retweeted_user=None
        self.retweet_status_id = 0
        self.is_reply = False
        self.in_reply_to_user = None
        self.in_reply_to_status_id = None
        
        self.retweet = None
        
        self.retweet_count = 0
        self.favourite_count = 0
        self.hashtags = []
        self.date = ''
        self.urls = []

        self.website_link = None

        if source=='twitter':
            self.from_twitter(tweet)

        elif source=='database':
            self.from_database(tweet)

    def from_twitter(self, tweet):
        self.tweet_id  = tweet.id
        self.user_id = tweet.user.id
        self.handle = tweet.user.screen_name
        self.date = tweet.created_at
        self.retweet_count = tweet.retweet_count
        self.favourite_count  = tweet.favorite_count

        self.website_link=u'https://twitter.com/'+self.handle+u'/status/'+str(self.tweet_id)
        
        if tweet.in_reply_to_user_id != None:
            #self.mentions.append((tweet.in_reply_to_user_id, tweet.in_reply_to_screen_name))
            self.is_reply = True
            self.in_reply_to_user = (tweet.in_reply_to_user_id,tweet.in_reply_to_screen_name)
            self.in_reply_to_status_id = tweet.in_reply_to_status_id

        if hasattr(tweet, 'retweeted_status'):
            tweet = tweet.retweeted_status
            self.retweeted_user = (tweet.user.id, tweet.user.screen_name)
            self.is_retweet = True
            self.retweet_status_id = tweet.id
            # self.retweeted_uid = tweet.user.id
            # self.mentions.append((tweet.user.id, tweet.user.screen_name))


        self.content = tweet.text
        self.mentions = [ (ent['id'],ent['screen_name'] 
                            ) for ent in tweet.entities['user_mentions'] ]
        self.hashtags =  [ent['text'] for ent in tweet.entities['hashtags']]
        self.urls = [urls['expanded_url'] for urls in tweet.entities['urls']]


    def __str__(self):
        return u'Tweet: %d %s || RC: %d || FC: %d || RT: %s || @ %s || # %s || Url %s\nContent: %s' %(
            self.tweet_id, self.handle, self.retweet_count, self.favourite_count,
            self.retweet, len(self.mentions), len(self.hashtags), len(self.urls),
            unicode(self.content) )

    def from_database(self, tweet):
        pass

    