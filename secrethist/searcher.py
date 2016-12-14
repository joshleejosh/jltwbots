import urllib, time, datetime
import jltw

def fetch_tweets(api, trend):
    te = trend.encode('utf-8')
    query = urllib.quote(te)
    rv = api.GetSearch(query, count=200)
    return rv

def count_tweets(api, trend):
    if not trend:
        return 0
    tweets = fetch_tweets(api, trend)
    time.sleep(1)
    ta = set()
    for tweet in tweets:
        #jltw.log(tweet.text)
        id = tweet.id
        if tweet.retweeted_status:
            id = tweet.retweeted_status.id
        ta.add(id)
    return len(ta)

def build_sample(api, trend, samples, sampwait):
    if not trend:
        return tuple()
    td = {}
    for i in xrange(samples):
        tweets = fetch_tweets(api, trend)
        jltw.log(trend, len(tweets), datetime.datetime.now())
        for tweet in tweets:
            #jltw.log(tweet.text)
            if tweet.retweeted_status:
                td[tweet.retweeted_status.id] = tweet.retweeted_status
            else:
                td[tweet.id] = tweet
        if i < samples-1:
            time.sleep(sampwait)
    jltw.log('Total unique tweets: %d'%len(td))
    time.sleep(1)

    rv = []
    for i in sorted(td.keys()):
        rv.append(td[i])

    return rv

