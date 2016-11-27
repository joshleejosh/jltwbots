import random
import mru

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

location_mru = []
def load_location_mru():
    global location_mru
    location_mru = mru.load_mru('location_mru')
def save_location_mru(newid):
    mru.save_mru('location_mru', newid)

def read_woes(api):
    url = '%s/trends/available.json' % (api.base_url)
    parameters = {}
    resp = api._RequestUrl(url, verb='GET', data=parameters)
    rv = api._ParseAndCheckTwitter(resp.content.decode('utf-8'))
    return rv

def find_woe(api, woeid):
    woes = read_woes(api)
    for woe in woes:
        if str(woe['woeid']) == woeid:
            return woe
    return None

def pick_woeid(api):
    woes = read_woes(api)
    candidates = []
    for woe in woes:
        if woe['parentid'] in MOSTLY_ENGLISH_SPEAKING and woe['woeid'] not in location_mru:
            candidates.append(woe)
    if not candidates:
        return DEFAULT_WOE
    rv = random.choice(candidates)
    print rv['name'], rv['woeid']
    return rv

def dump_woeids(api):
    woes = read_woes(api)
    for woe in woes:
        if woe['countryCode'] == 'US':
            print '%s, %s (%s)'%(woe['name'], woe['country'], woe['woeid'])

