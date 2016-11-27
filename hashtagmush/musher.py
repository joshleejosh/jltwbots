import os.path, random, unicodedata, codecs
from collections import defaultdict

WDIR = os.path.dirname(os.path.realpath(__file__))
NUM_TOPICS = 3
MIN_TWEETS = 2
NONSTOPCHARS = '#%$_'

stopwords = []
blacklist = []

def musher_init():
    load_stopwords()
    load_blacklist()
def load_file(fn):
    fp = codecs.open(os.path.join(WDIR, fn), encoding='utf-8')
    a = fp.read().split('\n')
    fp.close()
    return a
def load_stopwords():
    global stopwords
    stopwords.extend(load_file('stopwords'))
def load_blacklist():
    global blacklist
    blacklist.extend(load_file('blacklist'))

def is_stopchar(c):
    cat = unicodedata.category(c)
    if c in NONSTOPCHARS:
        return False
    if cat.startswith('L'): #letters
        return False
    if cat.startswith('N'): #numbers
        return False
    if cat in ('Cn', 'Co', 'Cs'): # emoji?
        return False
    return True

def is_stopword(w):
    w = w.upper()
    if w == 'RT':
        return True
    if w.startswith('@'):
        return True
    if w.startswith('.@'):
        return True
    if w.startswith('HTTP'):
        return True
    if w in stopwords:
        return True
    if w in blacklist:
        return True
    # deal with smart apostrophes
    if w.find(unichr(8217)) != -1:
        x = w.replace(unichr(8217), "'")
        if x in stopwords:
            return True
        if x in blacklist:
            return True
    return False

def is_stopword2(word, trend, location):
    def _cleanse(w):
        w = w.upper()
        if w.startswith('#'):
            w = w[1:]
        return w
    word = _cleanse(word)
    trend = _cleanse(trend)
    location = _cleanse(location)
    if word == trend: return False
    if word == location: return False
    if len(word) > len(trend):
        if word.find(trend) != -1: return False
    else:
        if trend.find(word) != -1: return False
    return True

def caseify(word):
    if word[0].islower():
        return word[0].upper() + word[1:]
    else:
        return word

def split_tweets(tweets, trend, location):
    rv = defaultdict(int)
    for tweet in tweets:
        a = tweet.text.split()
        for word in a:
            while word and is_stopchar(word[0]):
                word = word[1:]
            while word and is_stopchar(word[-1]):
                word = word[:-1]
            if word:
                if is_stopword(word):
                    continue
                if not is_stopword2(word, trend, location):
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
        # Within each bucket, deprioritize lowercase words.
        subbucketa = []
        subbucketb = []
        for w in buckets[c]:
            if w[0].islower():
                subbucketb.append(w)
            else:
                subbucketa.append(w)
        for w in subbucketa:
            rv.append(w)
        for w in subbucketb:
            rv.append(w)

    # filter out overlapping substrings, favoring the earlier entry (since it's more common).
    todel = []
    for i in xrange(0, len(rv)):
        wi = rv[i].upper()
        for j in xrange(i+1, len(rv)):
            wj = rv[j].upper()
            if len(wi) > len(wj):
                if wi.find(wj) != -1:
                    todel.append(j)
            else:
                if wj.find(wi) != -1:
                    todel.append(j)
    for i in reversed(sorted(todel)):
        try:
            del rv[i]
        except:
            # if I screwed up something with the array indexes, just move on.
            pass

    return rv

# Just pull out as many keywords as we can fit into a tweet.
def mushymushmush(tweets, trend):
    words = split_tweets(tweets, trend, 'America')
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

def listify(a):
    rv = ''
    if len(a) == 1:
        rv = '%s'%a[0]
    elif len(a) == 2:
        rv = '%s and %s'%(a[0], a[1])
    else:
        for i in xrange(len(a)-1):
            rv += '%s, '%caseify(a[i])
        rv += 'and %s'%caseify(a[-1])
    return rv

# Generate the title of my next book.
def secret_history(tweets, trend, location):
    words = split_tweets(tweets, trend, location)
    buckets = make_buckets(words, trend)
    filtered = sort_buckets(buckets)
    #print len(filtered), filtered

    # Don't just take the first 3, since they may be parts of a phrase.
    # Take the top 33%, shuffle *those*, then pick 3.
    n = max(len(filtered)/3, NUM_TOPICS)
    candidates = filtered[0:n]
    random.shuffle(candidates)
    topics = candidates[0:NUM_TOPICS]
    ts = listify(topics)
    rv = u'The Secret History of %s: %s in %s'%(trend, ts, location)
    return rv

if __name__ == '__main__':
    print listify(['Foo'])
    print listify(['Foo','Bar'])
    print listify(['Foo','Bar','Baz'])
    print listify(['Foo','Bar','Baz','Qux'])
    print listify(['Foo','Bar','Baz','Qux','Guh'])

