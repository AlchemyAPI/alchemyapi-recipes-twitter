#!/usr/bin/env python

import pymongo

l_client = pymongo.MongoClient()
l_client.twitter_db.tweets.drop()

print "Data from twitter_db instance has been deleted!"
