from __future__ import unicode_literals
import logging

from archipelago import Archipelago
from classes import Twirp, Tweet, TDBHandler

LOGGER = logging.getLogger(__name__)

def return_full_map(min_tweets=0, retweets_only=False, mentions_only=False):
    db_handler = TDBHandler()
    result = db_handler.get_full_map(min_tweets)

    return neo_to_d3map(result)

def return_party_nodes(party):
    db_handler = TDBHandler()
    result = db_handler.get_party_nodes(party)

    return neo_to_d3map(result)

def return_crossparty_nodes(partyA, partyB):
    db_handler = TDBHandler()
    result = db_handler.get_crossparty_nodes(partyA,partyB) 

    return neo_to_d3map(result)

# def return_neighbours():
#     db_handler = TDBHandler()
#     result = db_handler.get_neighbours()

#     return neo_to_d3map(result)

def neo_to_d3map(neo_map): 
    offical_id_list = [node.archipelago_id for node in neo_map]

    nodes = []
    for neo_node in neo_map:
        twirp = {
            "name": neo_node.name,
            "handle":neo_node.handle,
            "tweets": neo_node.tweets,
            "friends": neo_node.friends,
            "followers": neo_node.followers,
            "party": neo_node.party,
            "constituency": neo_node.constituency,
            "offices": neo_node.offices,
            "o_id": neo_node.archipelago_id,
            "clicked":0
        }

        retweeted, mentions, replies, by_proxy = {}, {}, {}, {}
        all_tweets, no_by_proxy = {}, {}

        for i, t in enumerate(neo_node.tweeted):
            url = neo_node.recent_url[i]
            count = neo_node.count[i]

            if t in all_tweets.keys():
                all_tweets[t][0] += count
                all_tweets[t][1] = url
            else:
                all_tweets[t] = [count, url]

            if neo_node.tweet_type[i] == u'MENTION':
                mentions.update({t:[count, url]})
            elif neo_node.tweet_type[i] == u'REPLY':
                replies.update({t:[count, url]})
            elif neo_node.tweet_type[i] == u'RETWEET':
                retweeted.update({t:[count, url]})
            
            if neo_node.tweet_type[i] == u'MENTION_BY_PROXY':
                by_proxy.update({t:[count, url]})
            elif t in no_by_proxy.keys():
                no_by_proxy[t][0] += count
                no_by_proxy[t][1] = url
            else:
                no_by_proxy[t] = [count, url]



        twirp.update( {"relationships":{
                                "mentions":mentions,
                                "retweets":retweeted,
                                "replies":replies,
                                "by_proxy":by_proxy,
                                "all_tweets":all_tweets,
                                "no_by_proxy":no_by_proxy
                            }
        })

        nodes.append(twirp)
    return {"nodes": nodes}

# This module is used to assimilate and clean the data provided in the 
# twirpy.db database. It is also used to isolate useful pieces of data and
# turn them into useful json files

# import sqlite3
# import time, sys, json, re 
# import unicodedata
# import operator
# import urlparse, httplib
# import requests
# from multiprocessing import Pool
# from nltk.corpus import stopwords
# import logging

# START_TIME = time.time()


# ##########################################
# # HIGHER ORDER DATA ASSIMILATION METHODS  (Generate maps, etc...)
# ##########################################

# def generate_map():
#     """Tale a list of twirps and for each:
#     -use mention_freq.json and retweet_freq.json 
# to generate a graph datastructure of communications
# Write map to JSON file.

# OUTPUT: {MPname: {"mentions":{JoeBloggs: 1, AnneClark:2, ...}, "retweets": {TimCook: 5, ...} }, ... }"""
#     stored_twirps = {handle for handle, _ in generate_stored_twirp_list()}
#     results = {}
#     lap_time()
#     with open('mention_freq.json', 'r') as m:
#         mentions = json.load(m)
#     with open('retweet_freq.json', 'r') as r:
#         retweets = json.load(r)

#     for name in stored_twirps:
#         print name
#         results[name] = {'retweets':{}, 'mentions':{}}
#         for mention in mentions[name].keys():
#             if mention in stored_twirps:
#                 results[name]['mentions'][mention] = mentions[name][mention]
#         for retweet in retweets[name].keys():
#             if retweet in stored_twirps:
#                 results[name]['retweets'][retweet] = retweets[name][retweet] 
                
#     with open('map.json', 'w') as f:
#         f.write(json.dumps(results))
#     lap_time()


# ##############################
# # LOWER ORDER JSON ASSIMILATION METHODS (Counting etc)
# ##############################

# def generate_url_frequency_json():
#     """Take list of twirps and for each:
#     - get list of urls tweeted or retweeted
#     - tally urls
# Write url frequency data to JSON file """ 
#     stored_names = generate_stored_twirp_list()
#     results = {}

#     for name, user_id in stored_names:
#         print name
#         tweet_list = select_entities_by_twirp(user_id, 'url')
#         results[name] = {}
  
#         for url in tweet_list:
#             if url[5] in results[name].keys():
#                 results[name][url[5]] +=1
#             else:
#                 results[name][url[5]] = 1

#     with open('url_freq.json', 'w+') as f:
#         f.write(json.dumps(results))
#     lap_time()

# def generate_retweet_frequency_json():
#     """Take list of twirps and for each:
#     - get list of retweet ids 
#     - tally retweet handles 
# Write retweet frequency data to JSON file """
#     stored_names = generate_stored_twirp_list()
#     results = {}

#     for name, user_id in stored_names:
#         print name
#         retweets = select_retweet_ids_by_twirp(user_id)
#         results[name] = {}

#         for tweet_ID, retweeted in retweets:
#             if retweeted in results[name].keys():
#                 results[name][retweeted] +=1
#             else:
#                 results[name][retweeted] =1

#     with open('retweet_freq.json', 'w+') as f:
#         f.write(json.dumps(results))
#     lap_time()

# def generate_hashtag_frequency_json():
#     """Take list of twirps and for each:
#     - get list of retweet ids
#     - get list of hashtags 
#     -tally hashtags, filtering out retweeted messages 
# Write hashtag frequency data to JSON file"""

#     stored_names = generate_stored_twirp_list()
#     results = {}

#     for name, user_id in stored_names:
#         print name
#         retweets = select_retweet_ids_by_twirp(user_id)
#         results[name] = {}
#         tweet_list = select_entities_by_twirp(user_id, 'hashtag')

#         for hashtag in tweet_list:
#             if hashtag[0] not in [x[0] for x in retweets]: 
#                 if hashtag[3].lower() in results[name].keys():
#                     results[name][hashtag[3].lower()] +=1
#                 else:
#                     results[name][hashtag[3].lower()] =1

#     with open('hashtag_freq.json', 'w+') as f:
#         f.write(json.dumps(results))
#     lap_time()

# def generate_mention_frequency_json():
#     """Take list of twirps and for each:
#     - get list of retweet ids 
#     - get list of mentioned entities
#     - tally mentioned entities, filtering out retweeted messages
# Write mention frequency data to JSON file """

#     stored_names = generate_stored_twirp_list()
#     results = {}

#     for name, user_id in stored_names:
#         print name
#         retweets = select_retweet_ids_by_twirp(user_id)
#         results[name] = {}
#         tweet_list = select_entities_by_twirp(user_id, 'mention')

#         for mention in tweet_list:
#             if mention[0] not in [x[0] for x in retweets]:
#                 if mention[3] in results[name].keys():
#                     results[name][mention[3]] +=1
#                 else:
#                     results[name][mention[3]] =1

#     with open('mention_freq.json', 'w+') as f:
#         f.write(json.dumps(results))
#     lap_time()
#     pass

# def generate_word_frequency_json():
#     """Take list of twirps, and for each:
#     - get list of tweets 
#     - filter out retweets
#     - tally words from all tweets' content in a dict, filtering out stopwords
# Write twirp word frequency data to single JSON file"""

#     stored_names = generate_stored_twirp_list()
#     results = {}

#     stop = stopwords.words('english')

#     tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
#                       if unicodedata.category(unichr(i)).startswith('P'))
    
#     for name, user_id in stored_names:
#         print name
#         results[name] = {}
#         tweet_list = select_tweets_by_twirp(user_id)

#         for tweet_record in tweet_list:
#             if tweet_record[5]=='NULL' or tweet_record[5]=='REPLY':
#                 words = tweet_record[4].translate(tbl)
#                 words = words.lower().split()
#                 for word in words:
#                     if word in results[name].keys():
#                         results[name][word] +=1
#                     else:
#                         results[name][word] = 1
    
#     filtered_results = {}
#     for name in results.keys():
#         filtered_results[name] = {word:results[name][word] for word in results[name].keys() if word not in stop}

#     with open('word_freq.json', 'w+') as f:
#         f.write(json.dumps(filtered_results))
#     lap_time()
#     pass

# ########################
# # DIRECT DATABASE QUERY METHODS
# ########################

# def generate_stored_twirp_list():
#     """Return a list of tuples, containing (TwitterHandles, UserID) from twirpy.db"""
#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT DISTINCT Userhandle, UserID FROM TweetData')
#         twirp_list = cur.fetchall()
#         return twirp_list

# def select_tweets_by_twirp(user_id):
#     """Return a list of tweet-info tuples from a certain user id: 
#     [ (UserId, UserHandle, Favourite Count, RetweetCount, Content, Retweet, CreatedDate, TweetID), ...]"""

#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT * FROM TweetData WHERE UserID=?', (user_id,))
#         return cur.fetchall()

# def select_entities_by_twirp(user_id, entity):
#     """Return a list of entities-info-tuples from a certain user id, and entity:
#  [ (TweetID, UserID, EntityType, Entity, ToUser, UrlBase), ...]"""

#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT * FROM TweetEntities WHERE UserID=? AND EntityType=?', (user_id,entity))
#         return cur.fetchall()

# def select_retweet_ids_by_twirp(user_id):
#     """Return a list of tuples of TweetIDs with Handles for all retweets by a user: 
# [ (TweetId, TwitterHandle),...]"""

#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT TwitterID, Retweet FROM TweetData \
#             WHERE UserID=? AND Retweet<>"NULL" AND Retweet<>"REPLY"', (user_id,))
#         return cur.fetchall()

# #############################
# # DATABASE ALTERING METHODS (CLEANING & OTHER)
# #############################

# def tally_retweets():
#     """UNBUILT: Tally up the total number of times a twirp has been retweeted,
# and update TwirpData"""
#     pass

# def tally_favourites():
#     """UNBUILT: Tally up the total number of times a twirp has been favourited,
# and update TwirpData"""
#     pass

# def clean_up_urls():
#     """For each url in database, call unshorten_url and parse_url, 
#     then update database with new url"""
#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT Entity, TweetID, UrlBase FROM TweetEntities WHERE EntityType="url"')
#         lap_time()

#     reg = re.compile('/{1}')

#     for i, (url, tweet_ID, url_base) in enumerate(cur.fetchall()):
#         print i, unicode(url), url_base

#         if url_base == None or url_base == '':
#             try: 
#                 url = unshorten_url(url)
#             except:
#                 print 'Error in Url Following'
#             try:
#                 base = parse_url(url)
#             except:
#                 print 'Error in Regex'
#             store_url(base, tweet_ID) 
#             print url
#         elif 'http' not in url_base:

#             try:
#                 base = parse_url(url)
#             except:
#                 print 'Error in Regex'
#             store_url(base, tweet_ID)
#             print url
#         else:
#             print url_base
    
#         connection.commit()

#         lap_time()

# def unshorten_url(url):
#     """Generate HEAD request of url to find 'unshortened url'
#      eg: 'bit.ly/i24rs -> google.com/hello"""

#     parsed = urlparse.urlparse(url)
#     http_obj = httplib.HTTPConnection(parsed.netloc)
#     http_obj.request('HEAD', parsed.path)
#     response = http_obj.getresponse()
#     if response.status/100 == 3 and response.getheader('Location'):
#         return response.getheader('Location')
#     else:
#         return url

# def parse_url(url):
#     """Find the base of the url, using regex"""
#     reg = re.compile('/')
#     reg_result = reg.split(url)
#     output = reg_result[0]+'//'+reg_result[2]
#     return output

# def store_url(url, tweet_ID):
#     """Store new url in database"""
#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('UPDATE TweetEntities SET UrlBase=?\
#                     WHERE TweetID=? AND EntityType="url"',(url, tweet_ID) )

# #################################
# #    CONTROL FLOW & UTILITY METHODS
# #################################


# def return_top_20():
#     """Print top 20 items from assimilated JSON for inspection purposes"""
#     list_length = 20
#     stored_names = generate_stored_twirp_list()

#     with open('hashtag_freq.json', 'r') as f:
#         hashtag_dict = json.load(f)
#     with open('mention_freq.json', 'r') as m:
#         mention_dict = json.load(m)
#     with open('word_freq.json', 'r') as w:
#         word_dict = json.load(w)
#     with open('retweet_freq.json', 'r') as r:
#         retweet_dict = json.load(r)
#     with open('url_freq.json', 'r') as u:
#         url_dict = json.load(u)

#     for name, user_id in stored_names:
#         sorted_hashtags = sorted(hashtag_dict[name].items(), key=operator.itemgetter(1), reverse=True)
#         sorted_mentions = sorted(mention_dict[name].items(), key=operator.itemgetter(1), reverse=True)
#         sorted_words = sorted(word_dict[name].items(), key=operator.itemgetter(1), reverse=True)
#         sorted_retweets = sorted(retweet_dict[name].items(), key=operator.itemgetter(1), reverse=True)
#         sorted_urls= sorted(url_dict[name].items(), key=operator.itemgetter(1), reverse=True)
#         print 'NAME: %s' %name, '\n'
        
#         top_h = sorted_hashtags[:list_length]
#         top_m = sorted_mentions[:list_length]
#         top_w = sorted_words[:list_length]
#         top_r = sorted_retweets[:list_length]
#         top_u = sorted_urls[:list_length]

#         if len(top_h)<list_length:
#             top_h.extend([(0,0)]*(list_length-len(top_h)))
#         if len(top_m)<list_length:
#             top_m.extend([(0,0)]*(list_length-len(top_m)))
#         if len(top_w)<list_length:
#             top_w.extend([(0,0)]*(list_length-len(top_w)))
#         if len(top_r)<list_length:
#             top_r.extend([(0,0)]*(list_length-len(top_r)))
#         if len(top_u)<list_length:
#             top_u.extend([(0,0)]*(list_length-len(top_u)))

#         template = "{0:5}|{1:25}{2:5}||{3:15}{4:5}||{5:15}{6:5}||{7:15}{8:5}||{9:30}{10:5}||"
    
#         print template.format('Order', 'HASHTAG','No.','WORDS','No.','MENTIONS','No.', 'RETWEETS', 'No.', "URLS", 'No.')
#         for i in range(0,list_length):
#             in_tuple = (i, top_h[i][0], top_h[i][1], top_w[i][0], top_w[i][1], top_m[i][0], 
#                         top_m[i][1], top_r[i][0], top_r[i][1], top_u[i][0], top_u[i][1])
#             try:
#                 print template.format(*in_tuple)
#             except:
#                 print 'Error'

#         print '\n\n\n'
#     lap_time()

# def monitor_twirps():
#     """ Print handle, number of tweets stored in database, total number of tweets
# ever tweeted for each twirp """

#     with sqlite3.connect('twirpy.db') as connection:
#         cur = connection.cursor()
#         cur.execute('SELECT COUNT(DISTINCT UserHandle) FROM TweetData')
#         mp_no = cur.fetchall()
#         print mp_no[0][0]
        
#         name_list = generate_stored_twirp_list()

#         for name, _  in name_list:

#             cur.execute('SELECT COUNT(*) FROM TweetData WHERE UserHandle=?', (name,))
#             tally = cur.fetchall()

#             cur.execute('SELECT TweetCount FROM TwirpData WHERE Handle=?', (name,))
#             tweet_count = cur.fetchall()

#             print name, '\t', tally[0][0], '\t', tweet_count[0][0]

# def lap_time():
#     '''Prints the time elapsed since the start of program running'''
#     lap = time.time()
#     print '---%s s ---' %(START_TIME-lap)

# def main():
#     '''Controls the flow of operations from cmd line'''
#     words = sys.argv
#     if len(words) ==1:
#         print 'print arg: [monitor, map]'
#     elif words[1]=='monitor':
#         monitor_twirps()
#     elif words[1]=='map':
#         generate_map()
#     elif words[1]=='twirp_list':
#         generate_stored_twirp_list()
#     elif words[1]=='word_freq':
#         generate_word_frequency_json()
#     elif words[1]=='hashtag':
#         generate_hashtag_frequency_json()
#     elif words[1]=='mention':
#         generate_mention_frequency_json()
#     elif words[1]=='top_20':
#         return_top_20()
#     elif words[1]=='retweets':
#         generate_retweet_frequency_json()
#     elif words[1]=='clean_urls':
#         clean_up_urls()

#     elif words[1]=='url':
#         generate_url_frequency_json()
#     elif words[1]=='refresh':
#         generate_word_frequency_json()
#         generate_hashtag_frequency_json()
#         generate_mention_frequency_json()
#         generate_retweet_frequency_json()
#         generate_url_frequency_json()

#     else:
#         print 'bad arguments'
    
# if __name__=='__main__':
#     main()