# jlj_ebooks takes tweet data from a JSON source file and generates gibberish using markov chains.

import argparse, json, random, xml.sax.saxutils
import jltw, jltw.twapi, jltw.markovator

CORPUS = []

def is_usable(w):
    if '@' in w:
        return False
    if w.startswith('http'):
        return False
    if w in ('RT', 'MT'):
        return False
    return True

def is_tweetable(a):
    s = ' '.join(a)
    # Keep things tweet sized.
    if len(s) > 140:
        return False
    # The shorter the phrase, the better chance it will just reconstruct an actual tweet.
    if len(a) < 6:
        return False
    # Did we accidentally recreate an original tweet?
    su = s.upper()
    hits = list(t for t in CORPUS if t.upper().find(su) != -1)
    if hits:
        jltw.log('OMG DUPLICATED ORIGINAL', [s,], hits)
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tweetfile', type=str, help='File containing tweet data to be markovized.')
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials.')
    parser.add_argument('num_tweets', nargs='?', default=1, type=int, help='Number of sentences to generate.')
    parser.add_argument('-t', '--tweet', dest='tweet', action='store_true', help='Post the result to twitter. If this is set, num_tweets is forced to 1 (to avoid rate errors)')
    args = parser.parse_args()

    fp = open(args.tweetfile)
    tweets = json.load(fp)
    fp.close()
    CORPUS = list(xml.sax.saxutils.unescape(tw['text']) for tw in tweets)
    m = jltw.markovator.Markovator((s.strip().split() for s in CORPUS), is_usable)

    api = None
    if args.tweet:
        api = jltw.twapi.open_twitter(args.authfile)
        args.num_tweets = 1

    for i in xrange(args.num_tweets):
        s = ' '.join(m.generate(is_tweetable))

        # Fix ending punctuation flakiness -- in particular, I tend to end a
        # tweet that contains a link with a colon instead of a period; since we
        # strip links out, the colon is left dangling.
        if s:
            c = s[-1]
            if c in (',', ';', ':'):
                s = s[:-1] + '.'

        if s and args.tweet:
            api.PostUpdate(s)
        jltw.log(s)

