# jlj_ebooks takes tweet data from a JSON source file and generates gibberish using markov chains.

import argparse, json, random, xml.sax.saxutils
import jltw

# #########################################################

CACHE_DELIM = '\v'
TERMINATOR = '\f'
CACHE = {}

def read_tweets(fn):
    tweets = []
    fp = open(fn)
    t = json.load(fp)
    fp.close()
    tweets.extend(t)

    for tweet in tweets:
        p = q = TERMINATOR
        a = tweet['text'].split()
        for word in a:
            word = word.encode('utf-8').strip()
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

def spew():
    rv = ''
    faili = 0
    while not is_tweetable(rv) and faili < 20:
        rv = chain()
        faili += 1

    # Fix ending punctuation flakiness -- in particular, I tend to end a tweet
    # that contains a link with a colon instead of a period; since we strip
    # links out, the colon is left dangling.
    if rv:
        c = rv[-1]
        if c in (',', ';', ':'):
            rv = rv[:-1] + '.'

    return rv

# #########################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tweetfile', type=str, help='File containing tweet data to be markovized.')
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials.')
    parser.add_argument('num_tweets', nargs='?', default=1, type=int, help='Number of sentences to generate.')
    parser.add_argument('-t', '--tweet', dest='tweet', action='store_true', help='Post the result to twitter. If this is set, num_tweets is forced to 1 (to avoid rate errors)')
    args = parser.parse_args()

    read_tweets(args.tweetfile)
    api = None
    if args.tweet:
        api = jltw.open_twitter(args.authfile)
        args.num_tweets = 1

    for i in xrange(args.num_tweets):
        s = spew()
        if args.tweet:
            api.PostUpdate(s)
        print s.decode('utf-8')

