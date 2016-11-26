import os.path, random, re, unicodedata, time, datetime
from collections import defaultdict

WDIR = os.path.dirname(os.path.realpath(__file__))
MIN_TWEETS = 2
NONSTOPCHARS = '#%$_'

stopwords = []
blacklist = []

def is_stopchar(c):
    if unicodedata.category(c).startswith('P'):
        if c not in NONSTOPCHARS:
            return True
    return False

def is_stopword(w):
    if w == 'RT':
        return True
    if w.startswith('@'):
        return True
    if w.startswith('.@'):
        return True
    if w.startswith('http'):
        return True
    if w.upper() in stopwords:
        return True
    if w.upper() in blacklist:
        return True
    return False

def load_file(fn):
    fp = open(os.path.join(WDIR, fn))
    a = fp.read().split('\n')
    fp.close()
    return a
def load_stopwords():
    global stopwords
    stopwords.extend(load_file('stopwords'))
def load_blacklist():
    global blacklist
    blacklist.extend(load_file('blacklist'))

def split_tweets(tweets):
    rv = defaultdict(int)
    for tweet in tweets:
        #print '------- %s %s'%(tweet.id, tweet.user.screen_name)
        #print tweet.text.encode('utf-8')
        a = tweet.text.split()
        for word in a:
            while word and is_stopchar(word[0]):
                word = word[1:]
            while word and is_stopchar(word[-1]):
                word = word[:-1]
            if word:
                if is_stopword(word):
                    continue
                rv[word] += 1
    return rv

def make_buckets(words, trend):
    rv = defaultdict(list)
    for word,count in words.iteritems():
        if count < MIN_TWEETS:
            continue
        if word.upper() == trend.upper():
            continue
        rv[count].append(word)
    for c in sorted(rv.keys()):
        rv[c].sort()
        s = ' '.join(rv[c]).encode('utf-8')
        print '%d: %s'%(c, s)
    return rv

# turn dict of words into an array sorted by reverse length; words of equal length bucket are randomly shuffled.
def sort_buckets(buckets):
    rv = []
    for c in reversed(sorted(buckets.keys())):
        random.shuffle(buckets[c])
        for w in buckets[c]:
            rv.append(w)
    return rv

def mushymushmush(tweets, trend):
    load_stopwords()
    load_blacklist()
    words = split_tweets(tweets)
    buckets = make_buckets(words, trend)
    preamble = u'%s: '%trend
    tlen = len(preamble)
    filtered = sort_buckets(buckets)
    for i,word in enumerate(filtered):
        if tlen + 1 + len(word.encode('utf-8')) > 140:
            del filtered[i:]
            break
        tlen += 1 + len(word.encode('utf-8'))
    #random.shuffle(filtered)
    rv = preamble + ' '.join(filtered)
    return rv

