class Twirp(object):
    twirps_type={
        "MP":0,
        "PartyOfficial":1,
        "Media":2,
        "ThinkTank":3,
    }

    def __init__(self, twitter_user, source):
        self.id = 0
        self.username = ''
        self.name = ''
        self.handle = ''
        self.followers_count = 0
        self.friends_count = 0
        self.tweet_count = 0
        self.retweet_count = 0
        self.been_retweet_count = 0 
        self.favourite_hashtag = ''
        self.hashtag_count = 0
        self.archipelago_id = 0 
        self.twirps_type = 0
        self.subscribed = False
        self.geo = False

        if source=='twitter':
            self.from_twitter(twitter_user)

        elif source=='database':
            self.from_database()

    def __str__(self):
        return u'||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
            self.handle, self.name, self.id, 
            self.followers_count, self.friends_count, self.geo )

    def from_twitter(self, twitter_user):
        self.id = twitter_user.id
        self.username = twitter_user.name
        self.handle = twitter_user.screen_name
        self.followers_count = twitter_user.followers_count
        self.friends_count = twitter_user.friends_count
        self.tweet_count = twitter_user.statuses_count
        self.geo = twitter_user.geo_enabled

    def from_database():
        pass
