import os.path, random, time
import jltw
import mrubuddy
import locator, searcher

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_FN = os.path.join(WDIR, 'trends.mru')

mru = None
def load_trend_mru():
    global mru
    mru = mrubuddy.MRU(MRU_FN)
    mru.load()
def save_trend_mru(newword):
    mru.save(newword)

def find_trends(api, woeid=1):
    rv = []
    trends = api.GetTrendsWoeid(woeid)
    time.sleep(1)
    for t in trends:
        #if t.name.startswith('#') and t.name not in trend_mru:
        if not t.name in mru:
            rv.append(t.name)
    if len(rv) == 0:
        jltw.log('ERROR: no trends!')
        return ''
    #jltw.log('%d Trends: %s'%(len(rv), ', '.join(rv))
    return rv

def find_trend(api, woeid=1):
    a = find_trends(api, woeid)
    return random.choice(a)

