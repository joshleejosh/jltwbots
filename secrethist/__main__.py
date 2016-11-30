# Find the top trending topic, query it, and spew out common words.

import argparse, time
import random
from collections import defaultdict
import jltw
import mru, locator, trendor, searcher, musher, htmarkov

NUM_SAMPLE_WOES = 7
NUM_SAMPLE_TRENDS = 3

# Handle cases where one or the other value is already known
def prejudge(api, trend, woeid):
    woe = None
    if woeid:
        woe = locator.find_woe(api, woeid)
    if woe and not trend:
        trend = trendor.find_trend(api, woe['woeid'])
    if trend and not woe:
        woe = locator.pick_woe(api)
    if woe and trend:
        return woe, woe['woeid'], trend
    return None, None, None

def find_params(api, trend=None, woeid=None):
    woe, woeid, trend = prejudge(api, trend, woeid)
    if woe and trend:
        return woe, trend

    # get some number of locations
    woes = locator.find_woes(api)
    c = len(woes)
    random.shuffle(woes)
    del woes[NUM_SAMPLE_WOES:]
    woes = {w['woeid']:w for w in woes}
    print '%d/%d: %s'%(len(woes), c, '; '.join((w['name'] for w in woes.values())).encode('utf-8'))

    # for each location, get trends
    woeTrends = {}
    trendCounts = defaultdict(int)
    for wid,w in woes.iteritems():
        a = trendor.find_trends(api, wid)
        print '%s (%d): %d trends'%(w['name'], w['woeid'], len(a))
        woeTrends[w['woeid']] = a
        for t in a:
            trendCounts[t] += 1

    # Filter out common trends, try to maintain local flavor
    conflicts = list(t for t in trendCounts.keys() if trendCounts[t] > 1)
    print 'Filter out %d conflicting trends'%len(conflicts)
    todel = []
    for w,a in woeTrends.iteritems():
        for i in xrange(len(a)-1, -1, -1):
            if a[i] in conflicts:
                del a[i]
        if len(a) == 0:
            todel.append(w)
    for w in todel:
        del woeTrends[w]
    if not woeTrends:
        return woe, trend
    for w,a in woeTrends.iteritems():
        print '%d: %d local trends'%(w, len(a))

    # Don't just pick the woe with the most unique trends: that will bias
    # towards non-US cities: US cities are far more common in the candidate
    # pool, and a lot of cities from a single country will have more conflicts.
    # Instead, randomly pick from woes with more than 1 hit.
    a = list(w for w in woeTrends.keys() if len(woeTrends[w])>1)
    if a:
        woeid = random.choice(a)
    if not woeid:
        woeid = random.choice(woeTrends.keys())

    # get some number of trends for this woe
    woe = woes[woeid]
    trends = woeTrends[woeid]
    c = len(trends)
    random.shuffle(trends)
    del trends[NUM_SAMPLE_TRENDS:]
    print '%s/%d: %d/%d: %s'%(woe['name'], woeid, len(trends), c, '; '.join(trends).encode('utf-8'))

    # Count tweets for each trend; pick the trend with the most tweets
    trendCounts = {}
    maxc=-1
    for t in trends:
        c = searcher.count_tweets(api, t)
        print '%s: %d tweets'%(t,c)
        trendCounts[t] = c
        if c > maxc:
            maxc = c
            trend = t

    # FINALLY, we have everything we need
    return woe, trend


def main(args):
    trendor.load_trend_mru()
    locator.load_location_mru()
    api = jltw.open_twitter(args.authfile)
    #print api.VerifyCredentials().screen_name
    #time.sleep(1)

    woe, trend = find_params(api, args.hashtag, args.woeid)
    woeid = 0
    if woe:
        woeid = woe['woeid']
        print '=======> %s %d: %s'%(woe['name'], woeid, trend)
    if not woe or not woeid or not trend:
        print 'FAILURE: Couldn\'t find parameter [%s] [%d] [%s]'%(woe, woeid, trend)
        return

    tweets = searcher.build_sample(api, trend, args.num_samples, args.sample_wait)
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

