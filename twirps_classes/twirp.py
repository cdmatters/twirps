import sqlite3

class Twirp(object):
    def __init__(self, twitter_user, source):
        self.statuses = 0
        self.followers_count = 0
        self.friends_count = 0
        self.geo = False
        self.id = 0
        self.username = ''
        self.name = ''
        self.handle = ''
        self.official_id = 0 
        self.retweet_count = 0
        self.been_retweet_count = 0 
        self.favourite_hashtag = 'NULL'
        self.hashtag_count = 0

        if source=='twitter':
            self.from_twitter(twitter_user)

        elif source=='database':
            self.from_database()

    def __str__(self):
        return u'||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
            self.handle, self.name, self.id, 
            self.followers_count, self.friends_count, self.geo )

    def from_twitter(self, twitter_user ):
        self.statuses = twitter_user.statuses_count
        self.followers_count = twitter_user.followers_count
        self.friends_count = twitter_user.friends_count
        self.geo = twitter_user.geo_enabled
        self.id = twitter_user.id
        self.username = twitter_user.name
        self.handle = twitter_user.screen_name
        self.official_id = 0

    def from_database():
        pass
