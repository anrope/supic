import nltk
import json
import requests
import urlparse
import urllib

def fetch_tweets(query):
	'''
	fetch tweets about the topic query, return a list of all
	words in the top num_tweets tweets
	'''
	
	num_tweets = 50
	
	r = requests.get('http://search.twitter.com/search.json', params = {'rpp': num_tweets, 'q': query})
	
	raw = json.loads(r.content)
	tokens = []
	if raw['results']:
		for r in raw['results']:
			tokens += [t for t in r['text'].lower().split(' ') if t]
	else:
		return ["supic: no tweets"]
		
	return tokens

def find_hashtags(tokens):
	'''
	find tokens that are twitter hashtags (#hashtag)
	'''
	
	hashtags = [token[1:] for token in tokens if token[0] == '#']
	print hashtags
	return hashtags
	
def purify(tokens):
	return [token.strip('.-/!@$%^&*()') for token in tokens]

def supic(env, start_response):
	'''
	WSGI method for parsing tweets about a submitted query
	'''
	
	start_response('200 OK', [('Content-Type', 'text/json')])
	
	query = urlparse.parse_qs(env['QUERY_STRING'])['query'][0]
	
	tokens = find_hashtags(fetch_tweets(query))
	
	freqdist = nltk.probability.FreqDist(tokens)
	words = freqdist.keys()
	
	#tagged = nltk.pos_tag(tokens)
	
	keyterms = {'keyterms': [{'token': words[i], 'count': freqdist[words[i]]} for i in range(min(3, len(words)))]}
	
	return json.dumps(keyterms)