alchemyapi-twitter-python
=========================

A simple example application that will connect to the Twitter API, run a search, gather tweets, and then calculate the sentiment of each Tweet using AlchemyAPI's text analysis functions for entity extraction and sentiment analysis.

For the walkthrough on how this software works, visit: http://www.alchemyapi.com/resources/tutorials/twitter-sentiment-analysis


#### Related Links ####

For more information on AlchemyAPI's sentiment analysis API: http://www.alchemyapi.com/products/features/sentiment-analysis/

For more information on AlchemyAPI's entity extraction API: http://www.alchemyapi.com/products/features/entity-extraction/


To try out all of AlchemyAPI's text analysis functions in an interactive web demo: http://www.alchemyapi.com/products/demo/


## Requirements ##

- An API key from AlchemyAPI (register for one at: http://www.alchemyapi.com/api/register.html)
- Credentials from Twitter - the Consumer Key and Consumer Secret (create a new application at: https://dev.twitter.com/apps)
- Python 2.7 (other versions of Python 2.x may work, Python 3.x will not)


## How to Configure ##

After obtaining your API key from AlchemyAPI and your credentials from Twitter, you'll need to configure the app to use them. 

To configure AlchemyAPI, run:

	python alchemyapi.py YOUR_API_KEY

Just replace YOUR_API_KEY will your 40 character API key from AlchemyAPI.


To configure your Twitter credentials, create a new file called 'config.py' and put these two lines in it:

	consumer_key = 'TWITTER_API_CONSUMER_KEY'
	consumer_secret = 'TWITTER_API_CONSUMER_SECRET'

where TWITTER_API_CONSUMER_KEY and TWITTER_API_CONSUMER_SECRET are the values obtained from https://dev.twitter.com/apps


## How to Run ##

Once you have everything configured, in your command window simply:

	python analyze.py "SEARCH_STRING" COUNT

where SEARCH_STRING is what to search Twitter for, and COUNT is the number of Tweets to attempt to gather. For example, try:

	python analyze.py "Denver Broncos" 150


## A Note About Security ##

There are several pieces of secret information needed for this application: your API key from AlchemyAPI and your Twitter API credentials. It is important that you keep this information safe and secret, and that means keeping them out of GitHub or other source code manager. The application expects these secret values to be in api_key.txt and config.py, respectively, and make sure you keep these files in your .gitignore file. DO NOT HARDCODE THEM INTO YOUR APPLICATION FILES.


## License ##

Copyright 2013 AlchemyAPI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

