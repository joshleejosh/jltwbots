# Find the top trending topic, query it, and spew out common words.

import argparse, os.path, random, re, unicodedata, time, datetime
from collections import defaultdict
import jltw
import musher, htmarkov

WDIR = os.path.dirname(os.path.realpath(__file__))

MRU_LEN = 10
WOEID = 23424977 #USA
SAMPLES = 4
SAMPLE_WAIT = 240
mru = []

def load_file(fn):
    fp = open(os.path.join(WDIR, fn))
    a = fp.read().split('\n')
    fp.close()
    return a
def load_mru():
    global mru
    mru.extend(load_file('mru'))

def save_mru(newword):
    if len(mru) > MRU_LEN:
        del mru[0]
    mru.append(newword)
    fp = open(os.path.join(WDIR, 'mru'), 'w')
    fp.write('\n'.join(mru))
    fp.close()

def find_trend(api):
    rv = []
    trends = api.GetTrendsWoeid(WOEID)
    for t in trends:
        if t.name.startswith('#') and t.name not in mru:
            rv.append(t.name)
    if len(rv) == 0:
        print 'ERROR: no trends!'
        return ''
    return random.choice(rv)

def build_sample(api, trend):
    if not trend:
        return tuple()
    rv = {}
    for i in xrange(SAMPLES):
        tweets = api.GetSearch(trend, count=200)
        print trend.encode('utf-8'), len(tweets), datetime.datetime.now()
        for tweet in tweets:
            rv[tweet.id] = tweet
        if i < SAMPLES-1:
            time.sleep(SAMPLE_WAIT)
    print 'Total unique tweets: %d'%len(rv)
    return rv.values()

def main(fn, tweetit):
    load_mru()
    api = jltw.open_twitter(fn)
    trend = find_trend(api)
    if trend:
        tweets = build_sample(api, trend)
        if len(tweets) > 0:
            text = musher.mushymushmush(tweets, trend)
            #text = htmarkov.spew(tweets, trend)
            if text:
                if tweetit:
                    api.PostUpdate(text)
                print text.encode('utf-8')
                save_mru(trend)
        else:
            print 'FAILURE: No tweets for trend [%s]'%trend

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials')
    parser.add_argument('-t', '--tweet', dest='tweet', action='store_true', help='Post the result to twitter. If this is set, num_tweets is forced to 1 (to avoid rate errors)')
    args = parser.parse_args()
    main(args.authfile, args.tweet)

