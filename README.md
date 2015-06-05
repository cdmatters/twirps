TWIRPS
======

The Twirps project is designed to provide two main functionalities:

1. The mass collection of tweets from British Members of Parliament into a structured database
2. The generation of interesting data, inferences and visualizations from this data


this more complete history of the working commits of this repo can be found [here](https://github.com/condnsdmatters/archipelago)

Requirements
------------
A twitter api oauth is required, available from the twitter dev website
The twitter addresses were supplied by the government

Current Functionality
---------------------

####Data & Code
+ *twirps_data_collection* is responsible for all data collection from Twitter
+ *twirps_data_assimilation* takes the raw data and generates some useful JSON
+ *twirps_data_investigation* provides analytical investigations of data using scikit and numpy

####Visualization
+ d3 force graph used to generate an intereactive map of tweets and retweets for MPs using 4 years data in run up to General Election 2015 
+ d3 divergent force graph showing the clusters from the kmeans data analysis investigations, but visually coloured by potential causes of clustering (party, geography, etc).  *in progress*

####Analysis
+ The K-Mean clustering algorithm is implemented in *twirps_data_assimilation*, designed to work on frequency json, to see if any natural clusterings form from data on hashtags, words, urls etc.  *refinement of model in progress*

Future Work
---------------
####Analysis
+ beyond simple tallies of favourite url links etc little analysis done. clustering on types of mps may yield some interesting results (indepedent-minded or party drive? left or right? nlp on type of language and party?)