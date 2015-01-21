#!/usr/bin/env python

import pymongo
import datetime



l_client = pymongo.MongoClient()
l_allTweets = l_client.twitter_db.tweets.find()
l_posTweets = l_client.twitter_db.tweets.find({"sentiment" : "positive"})
l_negTweets = l_client.twitter_db.tweets.find({"sentiment" : "negative"})
l_neuTweets = l_client.twitter_db.tweets.find({"sentiment" : "neutral"})


# Write positive tweet data
l_pos_score_file = open("scores.pos", "w")
l_pos_time_file  = open("times.pos", "w")
for l_tweet in l_posTweets:

    # Format the time string
    l_dateString = l_tweet['time'].replace("+0000 ", "")
    l_dateFormat = "%a %b %d %H:%M:%S %Y"
    l_outputDateString = datetime.datetime.strptime(l_dateString, l_dateFormat).strftime("%Y-%m-%d %H:%M:%S +0000")
    
    # Write out to the scores file
    l_pos_score_file.write("%.4f\n" % l_tweet['score'])

    # Write out to the times file
    l_pos_time_file.write("%s\n" % l_outputDateString)

l_pos_score_file.close()
l_pos_time_file.close()

# Write negative tweet data
l_neg_score_file = open("scores.neg", "w")
l_neg_time_file  = open("times.neg", "w")
for l_tweet in l_negTweets:

    # Format the time string
    l_dateString = l_tweet['time'].replace("+0000 ", "")
    l_dateFormat = "%a %b %d %H:%M:%S %Y"
    l_outputDateString = datetime.datetime.strptime(l_dateString, l_dateFormat).strftime("%Y-%m-%d %H:%M:%S +0000")

    # Write out to the scores file
    l_neg_score_file.write("%.4f\n" % l_tweet['score'])

    # Write out to the times file
    l_neg_time_file.write("%s\n" % l_outputDateString)

l_neg_score_file.close()
l_neg_time_file.close()
