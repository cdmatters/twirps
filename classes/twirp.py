class Twirp(object):
    def __init__(self, user, source):
        self.statuses = 0
        self.followers_count = 0
        self.friends_count = 0
        self.geo = False
        self.id = 0
        self.name = ''
        self.handle = ''
        self.official_id = 0 
        self.retweet_count = 0
        self.been_retweet_count = 0 
        self.favourite_hashtag = 'NULL'
        self.hashtag_count = 0

        if source=='twitter':
            self.from_twitter(user)

        elif source=='database':
            self.from_database(user)

    def __str__(self):
        return u'||%s : %s\n||Id %d; Fol %d; Fri %d; Geo %s ' % (
            self.handle, self.name, self.id, 
            self.followers_count, self.friends_count, self.geo )

    def from_twitter(self, user ):
        self.statuses = user.statuses_count
        self.followers_count = user.followers_count
        self.friends_count = user.friends_count
        self.geo = user.geo_enabled
        self.id = user.id
        self.name = user.name
        self.handle = user.screen_name
        self.official_id = 0

    def to_database(self):
        input_tuple =  (self.id, self.name, self.handle, self.followers_count, 
                        self.friends_count, self.statuses, self.retweet_count, 
                        self.been_retweet_count, self.favourite_hashtag,
                        self.hashtag_count, self.official_id)

        with sqlite3.connect('twirpy.db') as connection:
            cur = connection.cursor()
            cur.execute('INSERT OR REPLACE INTO TwirpData\
                        VALUES (?,?,?,?,?,?,?,?,?,?,?) ', input_tuple)


    def from_database(self, user):
        pass