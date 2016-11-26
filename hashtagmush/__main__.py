# Find the top trending topic, query it, and spew out common words.

import argparse, os.path, random, re, unicodedata, time, datetime
from collections import defaultdict
import jltw
import musher, htmarkov

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_LEN = 10
WOEID = 23424977 #USA
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
    if newword in mru:
        return
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

def build_sample(api, trend, samples, sampwait):
    if not trend:
        return tuple()
    rv = {}
    for i in xrange(samples):
        tweets = api.GetSearch(trend, count=200)
        print trend.encode('utf-8'), len(tweets), datetime.datetime.now()
        for tweet in tweets:
            if tweet.retweeted_status:
                rv[tweet.retweeted_status.id] = tweet.retweeted_status
            else:
                rv[tweet.id] = tweet
        if i < samples-1:
            time.sleep(sampwait)
    print 'Total unique tweets: %d'%len(rv)
    return rv.values()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('authfile',
            type=str,
            help='File containing Twitter credentials')
    parser.add_argument('hashtag',
            nargs='?',
            type=str,
            help='Topic to search for (instead of querying trends)')
    parser.add_argument('-t', '--tweet',
            action='store_true',
            dest='tweet',
            help='Post the result to twitter.')
    parser.add_argument('-sn', '--num-samples',
            action='store',
            dest='num_samples',
            type=int,
            default=1,
            help='Number of queries before processing')
    parser.add_argument('-sw', '--sample-wait',
            action='store',
            dest='sample_wait',
            type=int,
            default=60,
            help='Time between sample queries')
    args = parser.parse_args()

    load_mru()
    api = jltw.open_twitter(args.authfile)

    trend = args.hashtag
    if not trend:
        trend = find_trend(api)
    if not trend:
        print 'FAILURE: No trendng topics to search for'
        return

    tweets = build_sample(api, trend, args.num_samples, args.sample_wait)
    if len(tweets) > 0:
        text = musher.mushymushmush(tweets, trend)
        #text = htmarkov.spew(tweets, trend)
        if text:
            if args.tweet:
                api.PostUpdate(text)
            print text.encode('utf-8')
            save_mru(trend)
    else:
        print 'FAILURE: No tweets for trend [%s]'%trend

if __name__ == '__main__':
    main()

