import sqlite3

class Tweet(object):
    def __init__(self, tweet, source):
        self.tweetid = 0
        self.userid = 0
        self.handle = ''
        self.mentions = [] 
        self.content = ''
        self.retweet = 'NULL'
        self.retweet_count = 0
        self.favourite_count = 0
        self.hashtags = []
        self.date = ''
        self.urls = []

        if source=='twitter':
            self.from_twitter(tweet)

        elif source=='database':
            self.from_database(tweet)

    def from_twitter(self, tweet):
        self.tweetid  = tweet.id
        self.userid = tweet.user.id
        self.handle = tweet.user.screen_name
        self.date = tweet.created_at
        self.retweet_count = tweet.retweet_count
        self.favourite_count  = tweet.favorite_count
        
        if tweet.in_reply_to_user_id != None:
            #self.mentions.append((tweet.in_reply_to_user_id, tweet.in_reply_to_screen_name))
            self.retweet = 'REPLY'

        if hasattr(tweet, 'retweeted_status'):
            tweet = tweet.retweeted_status
            self.retweet = tweet.user.screen_name
            self.mentions.append((tweet.user.id, tweet.user.screen_name))

        self.content = tweet.text
        self.mentions = [ (ent['id'],ent['screen_name'] 
                            ) for ent in tweet.entities['user_mentions'] ]
        self.hashtags =  [ent['text'] for ent in tweet.entities['hashtags']]
        self.urls = [urls['expanded_url'] for urls in tweet.entities['urls']]


    def __str__(self):
        return u'Tweet %d %s || RC: %d || FC: %d || RT: %s || @ %s || # %s || Url %s\nContent: %s' %(
            self.tweetid, self.handle, self.retweet_count, self.favourite_count,
            self.retweet, len(self.mentions), len(self.hashtags), len(self.urls),
            unicode(self.content) )

    def from_database(self, tweet):
        pass

    def to_database(self):
        input_tuple = (self.userid, self.handle,  self.favourite_count, self.retweet_count,
            self.content, self.retweet,  self.date, self.tweetid )

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TweetData\
                        VALUES (?,?,?,?,?,?,?,?) ', input_tuple)
            for h in self.hashtags:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (self.tweetid, self.userid, 'hashtag', h))
            for u in self.urls:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,0,NULL)',
                    (self.tweetid, self.userid, 'url', u))
            for m in self.mentions:
                cur.execute('INSERT OR REPLACE INTO TweetEntities VALUES (?,?,?,?,?,NULL)',
                    (self.tweetid, self.userid, 'mention', m[1], m[0]))
