import random, time
import mru, locator, searcher

trend_mru = []
def load_trend_mru():
    global trend_mru
    trend_mru = mru.load_mru('trend_mru')
def save_trend_mru(newword):
    mru.save_mru('trend_mru', newword)

def find_trends(api, woeid=1):
    rv = []
    trends = api.GetTrendsWoeid(woeid)
    time.sleep(1)
    for t in trends:
        #if t.name.startswith('#') and t.name not in trend_mru:
        if not mru.in_mru('trend_mru', t.name):
            rv.append(t.name)
    if len(rv) == 0:
        print 'ERROR: no trends!'
        return ''
    #print '%d Trends: %s'%(len(rv), ', '.join(rv).encode('utf-8'))
    return rv

def find_trend(api, woeid=1):
    a = find_trends(api, woeid)
    return random.choice(a)

