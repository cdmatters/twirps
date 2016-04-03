TWIRPS
======
------

Twirps is a web app to explore echo chambers in the twitter-sphere in British politics. 


<!--The Twirps project is designed to provide two main functionalities:

1. The mass collection of tweets from British Members of Parliament into a structured database
2. The generation of interesting data, inferences and visualizations from this data


this more complete history of the working commits of this repo can be found [here](https://github.com/condnsdmatters/archipelago)-->

Requirements
------------
See [requirements.txt](https://github.com/condnsdmatters/twirps/blob/master/requirements.txt).  A sample of the technologies used are:

+ Web Framework: Flask 
+ Twitter Data: Tweepy
+ Political Data: [Archipelago](https://github.com/condnsdmatters/archipelago)
+ Visualisations: d3.js
+ Data Storage: postgres & neo4j

Tweepy requires a Twitter api oauth & key, available from the Twitter dev website.

Archipelago requires a They Work For You api, available from They Work For You dev website


About
-------------
###Current Functionality


A working web app is under construction. This will live update the data set, whilst also providing an engaging front end, and tools to explore the data.

This work can be found in the main **twirps** directory.

To be updated shortly. 

###Historical Fuctionality

This idea was born at the Recurse Centre in April/May `15 at the time of the British General Election.

Back then it was effectively 3 scripts for collecting, assimilating and investigating data, to generate static json and visualise data locally in the browser. This old code can still be found in the **historical** directory, along with some of the raw data.

#####Data & Code
+ *twirps_data_collection* is responsible for all data collection from Twitter
+ *twirps_data_assimilation* takes the raw data and generates some useful JSON
+ *twirps_data_investigation* provides analytical investigations of data using scikit and numpy

#####Visualization
+ d3 force graph used to generate an intereactive map of tweets and retweets for MPs using 4 years data in run up to General Election 2015 
+ d3 divergent force graph showing the clusters from the kmeans data analysis investigations, but visually coloured by potential causes of clustering (party, geography, etc).  *in progress*

#####Analysis
+ The K-Mean clustering algorithm is implemented in *twirps_data_assimilation*, designed to work on frequency json, to see if any natural clusterings form from data on hashtags, words, urls etc.  *refinement of model in progress*

RoadMap
-----------
####App
+ ~~build generic Flask backend~~
+ ~~move SQL -> graph database~~   *//maybe keep both*
+ ~~data collection methods~~
+ ~~rewrite d3 mapping js~~
+ find the best stories (investigate data set)
+ design UX & UI




Screenshots
-----------
##### 05/15

![all edges displayed](/historical/screenshots/contact_all_edges10.png?raw=True)

![names & total no of tweets displayed](/historical/screenshots/contact_names_tweets.png?raw=True)