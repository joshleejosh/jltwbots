# Find the top trending topic, query it, and spew out common words.

import argparse, time, datetime
from collections import defaultdict
import jltw
import mru, locator, trendor, musher, htmarkov

def build_sample(api, trend, samples, sampwait):
    if not trend:
        return tuple()
    rv = {}
    for i in xrange(samples):
        tweets = api.GetSearch(trend, count=200)
        print trend.encode('utf-8'), len(tweets), datetime.datetime.now()
        for tweet in tweets:
            #print tweet.text.encode('utf-8')
            if tweet.retweeted_status:
                rv[tweet.retweeted_status.id] = tweet.retweeted_status
            else:
                rv[tweet.id] = tweet
        if i < samples-1:
            time.sleep(sampwait)
    print 'Total unique tweets: %d'%len(rv)
    return rv.values()

def main(args):
    trendor.load_trend_mru()
    locator.load_location_mru()
    api = jltw.open_twitter(args.authfile)

    woe = None
    woeid = args.woeid
    if woeid:
        woe = locator.find_woe(api, woeid)
    if not woe or not woeid:
        woe = locator.pick_woeid(api)
        woeid = woe['woeid']
    if not woe or not woeid:
        print 'FAILURE: No locations to search for'
        return

    trend = args.hashtag
    if not trend:
        trend = trendor.find_trend(api, woeid)
    if not trend:
        print 'FAILURE: No trendng topics to search for'
        return

    musher.musher_init()
    tweets = build_sample(api, trend, args.num_samples, args.sample_wait)
    if len(tweets) > 0:
        #text = musher.mushymushmush(tweets, trend)
        text = musher.secret_history(tweets, trend, woe['name'])
        #text = htmarkov.spew(tweets, trend)
        if text:
            if args.tweet:
                api.PostUpdate(text)
            print text.encode('utf-8')
            trendor.save_trend_mru(trend)
            locator.save_location_mru(woeid)
    else:
        print 'FAILURE: No tweets for trend [%s]'%trend

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('authfile',
            type=str,
            help='File containing Twitter credentials')
    parser.add_argument('-t', '--tweet',
            action='store_true',
            dest='tweet',
            help='Post the result to twitter.')
    parser.add_argument('-w', '--woeid',
            action='store',
            dest='woeid',
            type=str,
            help='WOEID of location to search in (instead of querying)')
    parser.add_argument('-ht', '--hashtag',
            action='store',
            dest='hashtag',
            type=str,
            help='Topic to search for (instead of querying trends)')
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
    main(args)

