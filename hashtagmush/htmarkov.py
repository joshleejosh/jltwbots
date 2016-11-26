import argparse, random, xml.sax.saxutils
import jltw

# #########################################################

CACHE_DELIM = '\v'
TERMINATOR = '\f'
CACHE = {}

def read_text(tweets):
    for tweet in tweets:
        p = q = TERMINATOR
        text = tweet.text
        a = text.split()
        for word in a:
            word = word.strip()
            if not word:
                continue
            word = xml.sax.saxutils.unescape(word)
            if '@' in word or word.startswith('http') or word in ('RT', 'MT'):
                continue
            try:
                CACHE[(p,q)].append(word)
            except KeyError:
                CACHE[(p,q)] = [word]
            p = q
            q = word
        try:
            CACHE[(p,q)].append(TERMINATOR)
        except KeyError:
            CACHE[(p,q)] = [TERMINATOR]

# #########################################################

def is_tweetable(s):
    rv = True
    # Keep things tweet sized.
    if len(s) > 140:
        rv = False
    # The shorter the phrase, the better chance it will just reconstruct an actual tweet.
    if len(s.split()) < 6:
        rv = False
    return rv

def chain():
    p = q = TERMINATOR
    rv = nextword = ''
    while nextword != TERMINATOR:
        nextword = random.choice(list(CACHE[(p,q)]))
        rv += ' ' + nextword
        p = q
        q = nextword
    return rv.strip()

def spew(tweets, trend):
    read_text(tweets)
    #a = list(i for i in CACHE.values() if len(i) > 1)
    #print len(a), len(CACHE)

    preamble = '%s: '%trend
    rv = ''
    faili = 0
    while not is_tweetable(rv) and faili < 20:
        rv = preamble + chain()
        faili += 1

    # Fix ending punctuation flakiness
    if rv:
        c = rv[-1]
        if c in (',', ';', ':'):
            rv = rv[:-1] + '.'

    return rv

