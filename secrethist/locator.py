import os.path, random, time
import jltw.mru

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_FN = os.path.join(WDIR, 'locations.mru')

WOEID_US = 23424977
DEFAULT_WOE = {
        u'country': u'United States',
        u'countryCode': u'US',
        u'name': u'United States',
        u'parentid': 1,
        u'placeType': {u'code': 12, u'name': u'Country'},
        u'url': u'http://where.yahooapis.com/v1/place/23424977',
        u'woeid': 23424977
        }

MOSTLY_ENGLISH_SPEAKING = (
        23424748, # Australia
        23424775, # Canada
        23424803, # Ireland
        23424916, # New Zealand
        23424975, # United Kingdom
        23424977, # United States
        )

WOEIDS={}

mru = None
def load_location_mru():
    global mru
    mru = jltw.mru.MRU(MRU_FN)
    mru.load()
def save_location_mru(newid):
    mru.save(newid)

def _read_woes(api):
    url = '%s/trends/available.json' % (api.base_url)
    parameters = {}
    resp = api._RequestUrl(url, verb='GET', data=parameters)
    rv = api._ParseAndCheckTwitter(resp.content.decode('utf-8'))
    time.sleep(1)
    return rv

def find_woe(api, woeid):
    woes = _read_woes(api)
    for woe in woes:
        if str(woe['woeid']) == woeid:
            return woe
    return None

def find_woes(api):
    woes = _read_woes(api)
    rv = []
    for woe in woes:
        if woe['parentid'] in MOSTLY_ENGLISH_SPEAKING and not woe['woeid'] in mru:
            rv.append(woe)
    if not rv:
        rv.append(DEFAULT_WOE)
    #print ' '.join((i['name'] for i in candidates)).encode('utf-8')
    return rv

def pick_woe(api):
    candidates = find_woes(api)
    rv = random.choice(candidates)
    print rv['name'], rv['woeid']
    return rv

def dump_woeids(api):
    woes = _read_woes(api)
    for woe in woes:
        if woe['countryCode'] == 'US':
            print '%s, %s (%s)'%(woe['name'], woe['country'], woe['woeid'])

