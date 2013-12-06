#!/usr/bin/env python

#	Copyright 2013 AlchemyAPI
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import sys
import json
import base64
import urllib2
import urllib
from alchemyapi import AlchemyAPI

try:
	import config
except ImportError:
	print '\nError finding Twitter credentials in config.py, please add them'
	f = open('config.py','w+')
	f.write("consumer_key='TWITTER_API_CONSUMER_KEY'\n")
	f.write("consumer_secret='TWITTER_API_CONSUMER_SECRET'\n")
	f.close()
	sys.exit()


def oauth():
	"""
	Connect with the Twitter API to request the OAuth access token.
	The token will be used to authorize the Twitter API search.

	INPUT:
	config.consumer_key -> the Twitter API consumer key, stored in config.py
	config.consumer_secret -> the Twitter API consumer secret, stored in config.py

	OUTPUT:
	auth.access_token -> the token
	auth.token_type -> the type of token (i.e. bearer)
	"""


	print ''
	print 'Requesting OAuth token from Twitter API'

	try:
		#Twitter credientials
		consumer_key = config.consumer_key
		consumer_secret = config.consumer_secret 

		#encode the credentials & setup the request
		encoded = base64.b64encode(consumer_key + ':' + consumer_secret)
		url = 'https://api.twitter.com/oauth2/token'
		params = { 'grant_type':'client_credentials' }
		headers = { 'Authorization':'Basic ' + encoded }

		#create the request and hit the Twitter API
		request = urllib2.Request(url, urllib.urlencode(params), headers)
		response = json.loads(urllib2.urlopen(request).read())

		#save the token
		auth = {}
		auth['access_token'] = response['access_token']
		auth['token_type'] = response['token_type']
		
		print 'Received token'
		print ''
		return auth
	except Exception as e:
		print 'Twitter authentication failed: ', e
		sys.exit()


def search(auth, query, number_of_tweets):
	"""
	Using the auth token, hit the Twitter search API with the specified
	query and attempt to return the requested number of tweets. If the 
	requested number of tweets can not be found, it will return as many
	as Twitter will provide.

	The Twitter response data contains many fields, and the returned data
	is filtered to only return the fields specified in the code.
	
	It will ignore retweets, defined as tweets starting with 'RT '.

	INPUT:
	auth -> the authentication token and token type from the OAuth process
	query -> the query to search Twitter for (i.e. "Denver Broncos")
	number_of_tweets -> the number of tweets to attempt to gather

	OUTPUT:
	tweets -> an array of tweets containing the filtered field set	
	"""

	#create the search request
	url = 'https://api.twitter.com/1.1/search/tweets.json'
	headers = { 'Authorization': auth['token_type'] + ' ' + auth['access_token'] }
	tweets = []
	MAX_PAGE_SIZE = 100
	counter = 0
	next_results = ''
	
	print 'Searching Twitter to try and find %d Tweets about "%s"' % (number_of_tweets, query)

	#keep getting more data until the number of tweets have been gathered
	while True: 
		print 'performing a search iteration, found %d Tweets thus far' % len(tweets)
		count = max(MAX_PAGE_SIZE,int(number_of_tweets) - counter)

		#create the request
		if next_results:
			request = urllib2.Request(url + next_results, headers=headers)
		else:
			params = { 'q':query, 'lang':'en','count':count }
			request = urllib2.Request(url + '?' + urllib.urlencode(params), headers=headers)

		#hit the Twitter API
		data = json.loads(urllib2.urlopen(request).read())

		#Scan through the Tweets and save the important information
		for status in data['statuses']:
			text = status['text'].encode('utf-8')
			
			#ignore retweets (RT at start of text)
			if text.find('RT ') != 0:
				#save the important info (save more fields here as needed)
				tweet = {}
				tweet['text'] = text
				tweet['screen_name'] = status['user']['screen_name']
				tweet['created_at'] = status['created_at']		
				tweets.append(tweet)
				counter += 1
				
				#check if we've grabbed enough tweets, exit if yes
				if counter >= number_of_tweets:
					print 'Found all %d Tweets!' % number_of_tweets
					return tweets

		#setup the next iteration
		if 'next_results' in data['search_metadata']:
			next_results = data['search_metadata']['next_results']
		else:
			#if next_results is not present, it means Twitter has no more data for us, so move on
			print 'Sorry, I could only find %d Tweets instead of %d' % (counter, number_of_tweets)
			return tweets


def process(query, in_queue, out_queue):
	"""
	The worker thread to grab a found Tweet off the queue and 
	calculate the sentiment via AlchemyAPI. 

	It calculates the document-level sentiment for the entire tweet, and
	it will also attempt to calculate entity-level sentiment if the query
	string is identified as an entity. If the query string is not 
	identified as an entity for the tweet, no entity level sentiment
	will be returned.
	
	INPUT:
	query -> the query string that was used in the Twitter API search (i.e. "Denver Broncos")
	in_queue -> the shared input queue that is filled with the found tweets.
	out_queue -> the shared output queue that is filled with the analyzed tweets.

	OUTPUT:
	None	
	"""

	#Create the AlchemyAPI object
	alchemyapi = AlchemyAPI()
	
	while True:
		#grab a tweet from the queue
		tweet = in_queue.get()	
		
		#init
		tweet['sentiment'] = {}

		try:
			#calculate the sentiment for the entity
			response = alchemyapi.entities('text',tweet['text'], { 'sentiment': 1 })
			if response['status'] == 'OK':
				for entity in response['entities']:
					#Check if we've found an entity that matches our query
					if entity['text'] == query:
						tweet['sentiment']['entity'] = {}
						tweet['sentiment']['entity']['type'] = entity['sentiment']['type']
						
						#Add the score (it's not returned if type=neutral)
						if 'score' in entity['sentiment']:
							tweet['sentiment']['entity']['score'] = entity['sentiment']['score']
						else:
							tweet['sentiment']['entity']['score'] = 0  
						
						#Only 1 entity can possibly match the query, so exit the loop
						break

			#calculate the sentiment for the entire tweet
			response = alchemyapi.sentiment('text',tweet['text'])

			if response['status'] == 'OK':
				tweet['sentiment']['doc'] = {}
				tweet['sentiment']['doc']['type'] = response['docSentiment']['type']
				
				#Add the score (it's not returned if type=neutral)
				if 'score' in response['docSentiment']:
					tweet['sentiment']['doc']['score'] = response['docSentiment']['score']
				else:
					tweet['sentiment']['doc']['score'] = 0  
			
			#add the result to the output queue
			out_queue.put(tweet)
		
		except Exception as e:
			#if there's an error, just move on to the next item in the queue
			print 'Uh oh, this just happened: ', e
			pass
			
		#signal that the task is complete
		in_queue.task_done()



def analyze(tweets, query):
	"""
	Spawns the thread pool and watches for the threads to finish processing
	the input queue. Once complete, it unloads the output queue into an array
	and passes it on for further processing.

	The number of threads is set to CONCURRENCY_LIMIT, which is the maximum 
	number of concurrent processes allowed by AlchemyAPI for your plan. The
	concurrency limit is 5 for the free plan.

	INPUT:
	tweets -> an array containing the tweets to analyze. 
	query -> the query string that was used in the Twitter API search (i.e. "Denver Broncos")

	OUTPUT:
	tweets -> an array containing the analyzed tweets	
	"""

	import Queue
	import threading

	#number of parallel threads to run to hit AlchemyAPI concurrently (higher is faster, the limit depends on your plan)
	CONCURRENCY_LIMIT = 5

	#init
	in_queue = Queue.Queue()
	out_queue = Queue.Queue()

	#load up the in_queue
	for tweet in tweets:
		in_queue.put(tweet)
	
	#Spawn and start the threads
	threads = []
	for x in xrange(CONCURRENCY_LIMIT):
		t = threading.Thread(target=process, args=(query, in_queue, out_queue))
		t.daemon = True
		threads.append(t)
		t.start()

	#init the display
	print ''
	print ''
	print 'Calculating sentiment for each tweet'	
	print ''
	
	#Wait until the input queue is empty
	while True:
		#print the counter
		sys.stdout.write('Tweets left to analyze: {0}                   \r'.format(in_queue.qsize()))
		sys.stdout.flush()

		#check if the queue has been emptied out
		if in_queue.empty():
			break
			
		#Check if the threads are still alive	
		check = False	
		for t in threads:
			if t.isAlive():
				check = True
				break

		if not check:
			#All threads have died, so quit
			break
		
	print 'Done analyzing!'

	#pull the data off the out_queue
	output = []
	while not out_queue.empty():
		output.append(out_queue.get())

	#return the tweets with the appended data
	return output


def output(tweets):
	"""
	Prints the found tweets and the sentiment.

	INPUT:
	tweets -> an array containing the analyzed tweets. 

	OUTPUT:
	None	
	"""
	if len(tweets) == 0:
		print 'No tweets found'
		sys.exit()
	
	print ''
	print ''
	print '##########################################################'
	print '#    The Tweets                                          #'
	print '##########################################################'
	print ''
	print ''

	for tweet in tweets:
		print '@' + tweet['screen_name']
		print 'Date: ' + tweet['created_at']
		print tweet['text']
		
		if 'entity' in tweet['sentiment']:
			print 'Entity Sentiment:', tweet['sentiment']['entity']['type'], '(Score:', str(tweet['sentiment']['entity']['score']) + ')'

		if 'doc' in tweet['sentiment']:
			print 'Document Sentiment:', tweet['sentiment']['doc']['type'], '(Score:', str(tweet['sentiment']['doc']['score']) + ')'

		print ''



def stats(tweets):
	"""
	Calculate and print out some basic summary statistics

	INPUT:
	tweets -> an array containing the analyzed tweets
	
	OUTPUT:
	None
	"""

	#init
 	data = {}
	data['doc'] = {}
	data['doc']['positive'] = 0
	data['doc']['negative'] = 0
	data['doc']['neutral'] = 0
	data['doc']['total'] = 0
	
	data['entity'] = {}
	data['entity']['positive'] = 0
	data['entity']['negative'] = 0
	data['entity']['neutral'] = 0
	data['entity']['total'] = 0
	
	#loop through the tweets and count up the positive, negatives and neutrals
	for tweet in tweets:
		if 'entity' in tweet['sentiment']:
			data['entity'][tweet['sentiment']['entity']['type']] += 1
			data['entity']['total'] += 1

		if 'doc' in tweet['sentiment']:
			data['doc'][tweet['sentiment']['doc']['type']] += 1
			data['doc']['total'] += 1

	#Make sure there are some analyzed tweets
	if data['doc']['total'] == 0 and data['entity']['total'] == 0:
		print 'No analysis found for the Tweets'
		sys.exit()

	#print the stats
	print ''
	print ''
	print '##########################################################'
	print '#    The Stats                                           #'
	print '##########################################################'
	print ''
	print ''
	
	if data['entity']['total'] > 0:
		print 'Entity-Level Sentiment:'
		print 'Positive: %d (%.2f%%)' % (data['entity']['positive'], 100.0*data['entity']['positive']/data['entity']['total'])
		print 'Negative: %d (%.2f%%)' % (data['entity']['negative'], 100.0*data['entity']['negative']/data['entity']['total'])
		print 'Neutral: %d (%.2f%%)' % (data['entity']['neutral'], 100.0*data['entity']['neutral']/data['entity']['total'])
		print 'Total: %d (%.2f%%)' % (data['entity']['total'], 100.0*data['entity']['total']/data['entity']['total'])
		print ''
		print ''
	
	if data['doc']['total'] > 0:
		print 'Document-Level Sentiment:'
		print 'Positive: %d (%.2f%%)' % (data['doc']['positive'], 100.0*data['doc']['positive']/data['doc']['total'])
		print 'Negative: %d (%.2f%%)' % (data['doc']['negative'], 100.0*data['doc']['negative']/data['doc']['total'])
		print 'Neutral: %d (%.2f%%)' % (data['doc']['neutral'], 100.0*data['doc']['neutral']/data['doc']['total'])
		print 'Total: %d (%.2f%%)' % (data['doc']['total'], 100.0*data['doc']['total']/data['doc']['total'])


def main(query, count):
	"""
	The main script the calls each of the functions as needed.

	INPUT:
	query -> the query string to use to search the Twitter API and for finding entities
	count -> the number of Tweets to attempt to gather from the Twitter API

	OUTPUT:
	None
	"""

	auth = oauth()
	tweets = search(auth, query, count)
	tweets = analyze(tweets, query)
	output(tweets)
	stats(tweets)



#Check the command line arguments
if not len(sys.argv) == 3:
	print "Invalid number of input arguments. Please run 'python analyze.py \"QUERY_STRING\" COUNT'"
	print "Where QUERY_STRING is what to search for (i.e. 'Denver Broncos')"
	print "And COUNT is the number of Tweets to attempt to gather\n"
	sys.exit()

#run the script
main(sys.argv[1], int(sys.argv[2]))




