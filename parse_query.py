import nltk
import json
import requests
import urlparse
import urllib

"""
Playing around with twisted, nltk, twitter, flickr, ajax,
jquery, twitter bootstrap.

Things to try:
	- display images linked in tweets (popular ones?)
	- find ngrams
	- find most common nouns/verbs

mobile/web app for crowdsourced tag annotation of tweets (!)
"""

class Supic:
	""" 
	Using an instance of this class as the WSGI application
	callable allows us to initialize some things that will
	persist throughout the life of the WSGI process
	"""
	def __init__(self):
		"""
		train our taggers.

		In the future, maybe pickle and load from file the trained tagger
		"""
		trainset = './twpos-data-v0.2/train'
		trainfile = open(trainset, 'r')

		train_tweets = []
		tweet = []
		for line in trainfile:
			if line == '\n':
				train_tweets.append(tweet)
				tweet = []
			else:
				tweet.append(tuple(line.lower().strip('\n').split('\t')))

		default_tagger = nltk.tag.sequential.DefaultTagger('N')
		unigram_tagger = nltk.tag.sequential.UnigramTagger(
			train_tweets, 
			backoff=default_tagger)
		bigram_tagger = nltk.tag.sequential.BigramTagger(
			train_tweets,
			backoff=unigram_tagger)
		regex_tagger = nltk.tag.sequential.RegexpTagger([
			(r'^http://', 'U'),
			(r'^@', '@'),
			(r'^#', '#')],
			backoff=bigram_tagger)

		self.tagger = regex_tagger

	def __call__(self, env, start_response):
		return supic(env, start_response, self.tagger)

def fetch_tweets(query):
	"""
	fetch tweets about the topic query, return a list of all
	words in the top num_tweets tweets
	"""
	num_tweets = 50
	
	r = requests.get(
		'http://search.twitter.com/search.json', 
		params = {'rpp': num_tweets, 'q': query})
	
	raw = json.loads(r.content)
	tokens = []
	if raw['results']:
		for r in raw['results']:
			tokens.append([t for t in r['text'].lower().split(' ')])
	else:
		return ["supic: no tweets"]
		
	return tokens

def find_hashtags(tweets):
	"""	find tokens that are twitter hashtags (#hashtag) """
	return [(tweet, tok) 
		for tweet in range(len(tweets))
		for tok in range(len(tweets[tweet]))
		if tweets[tweet][tok].startswith('#')]

def find_urls(tweets):
	""" find tokens that are urls """
	return [(tweet, tok) 
		for tweet in range(len(tweets))
		for tok in range(len(tweets[tweet]))
		if tweets[tweet][tok].startswith('http://')]
	
def find_users(tweets):
	""" find tokens that are users """
	return [(tweet, tok) 
		for tweet in range(len(tweets))
		for tok in range(len(tweets[tweet]))
		if tweets[tweet][tok].startswith('@')]

def purify(tweets):
	tweets = [[tok.strip('.-/!@$%^&*()\n_"\':')
		for tok in tweet]
		for tweet in tweets]
	return [[tok for tok in tweet if tok] for tweet in tweets]

def find_popular(itemrefs, tweets, popular=3, num_items=3):
	""" finds the num_items most popular (frequency > popular) items """
	items = [tweets[tweet][tok] for tweet, tok in itemrefs]
	itemfreq = nltk.probability.FreqDist(items)
	keys = itemfreq.keys()
	return [keys[i] for i in range(min(num_items, len(keys))) if itemfreq[keys[i]] >= popular]

def extract_info(tweets):
	""" extract users, hashtags, and urls from tweets """
	hashtags = find_hashtags(tweets)
	urls = find_urls(tweets)
	users = find_users(tweets)
	tweets = purify(tweets)

	return tweets, hashtags, users, urls

def tag_tweets(tweets, tagger):
	""" assign pos tags to words in tweets """
	tagged_tweets = []
	for tweet in tweets:
		tagged_tweets.append(tagger.tag(tweet))
	return tagged_tweets

def supic(env, start_response, tagger):
	""" WSGI method for parsing tweets about a submitted query """
	start_response('200 OK', [('Content-Type', 'text/json')])

	querystring = urlparse.parse_qs(env['QUERY_STRING'])
	if querystring.has_key('query'):
		query = urlparse.parse_qs(env['QUERY_STRING'])['query'][0]
	else:
		return None
	
	raw_tweets = fetch_tweets(query)

	tweets, hashtags, users, urls = extract_info(raw_tweets)

	popular_urls = find_popular(urls, raw_tweets)

	tagged_tweets = tag_tweets(raw_tweets, tagger)

	print tagged_tweets[1:2][:10]

	#stemmer = nltk.PorterStemmer()
	#tokens = [stemmer.stem(tok) for tweet in tweets for tok in tweet]

	freqdist = nltk.probability.FreqDist([tok for tweet in tweets for tok in tweet])
	words = freqdist.keys()

	keyterms = {
		'keyterms': [{
			'token': words[i], 
			'count': freqdist[words[i]]}
			for i in range(min(3, len(words)))],
		'popurls': popular_urls}
	
	print keyterms
	print

	return json.dumps(keyterms)
