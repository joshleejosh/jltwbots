# encoding: utf-8
# dognamer replies to tweets with a name for your dog.

import random, time, os.path
import jltw, jltw.twapi, jltw.shuffler, jltw.mru
import markovator

VERBOSE = False
DEFAULT_DELAY = 10 # seconds

DOGNAMES_FN = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'botdata', 'dognames.txt'))
MORDER = 4

PREFIX='Good names for a good dog:\n'


# ######################################################## #

def read_mentions(api, lastid):
    tweets = api.GetMentions(since_id=lastid, count=100)
    if VERBOSE:
        jltw.log('found', len(tweets))
    return tweets

# Only reply to tweets that mention dogs or post a picture (of a dog, presumably)
def should_reply(tweet):
    print(tweet.media)
    return True

def make_markovator():
    rv = None
    with open(DOGNAMES_FN) as fp:
        # read the data file: one item per line, each line split
        # into a list of letters (rather than words)
        data = [list(s.strip()) for s in fp.readlines()]
        rv = markovator.Markovator(data, order=MORDER)
    return rv

def make_body(mark, mrunames, numnames):
    def ffilter(w):
        w = ''.join(w)
        u = w.upper()
        for n in mark.corpus:
            n = ''.join(n).upper()
            if n.find(u) != -1:
                return False
        if w in mrunames:
            return False
        return True

    names = []
    for _ in range(numnames):
        n = mark.generate(filter=ffilter)
        n = ''.join(n)
        names.append(n)
        mrunames.add(n)
    text = PREFIX
    text += '\n'.join(['%d. %s'%(i+1,n) for i,n in enumerate(names)])
    return text

# ######################################################## #

def make_bare(api, mark, mrunames, numnames, dotweet):
    body = make_body(mark, mrunames, numnames)
    jltw.log('----')
    jltw.log(body)
    if dotweet:
        api.PostUpdate(body)

def make_replies(api, mark, mrutweets, mrunames, numreplies, numnames, delay, dotweet):
    lastid = None
    if len(mrutweets) > 0:
        lastid = mrutweets[-1]

    mentions = read_mentions(api, lastid)
    nmentions = len(mentions)
    if VERBOSE:
        jltw.log(u'found [%d] mentions'%nmentions)
        for m in mentions:
            jltw.log(u'[%s]'%m.text)

    if len(mentions) > 0:
        nmentions = 0
        while nmentions < numreplies and len(mentions) > 0:
            mention = random.choice(mentions)
            mentions.remove(mention)
            if mention.id_str in mrutweets:
                continue
            mrutweets.add(mention.id_str)
            if not should_reply(mention):
                continue

            body = make_body(mark, mrunames, numnames)
            body = '@%s %s'%(mention.user.screen_name, body)
            jltw.log(body)

            if dotweet:
                api.PostUpdate(body, in_reply_to_status_id=mention.id_str)
            nmentions += 1
            time.sleep(delay)

        if VERBOSE:
            jltw.log('----')
            jltw.log('Replied to %d/%d'%(nmentions, numreplies))


# ######################################################## #

if __name__ == '__main__':
    import argparse, codecs, json
    parser = argparse.ArgumentParser()
    parser.add_argument('credentials',
            type=str,
            help='file containing twitter credentials')
    parser.add_argument('--num-replies',
            dest='numreplies',
            action='store',
            type=int,
            default=0,
            help='number of tweets replied to')
    parser.add_argument('--num-names',
            dest='numnames',
            action='store',
            type=int,
            default=1,
            help='number of names generated')
    parser.add_argument('--delay',
            dest='delay',
            action='store',
            type=int,
            default=DEFAULT_DELAY,
            help='time between replies')
    parser.add_argument('--mru-tweets',
            dest='mrutweets',
            action='store',
            type=str,
            default='',
            help='file containing MRU list for tweets replied to')
    parser.add_argument('--mru-names',
            dest='mrunames',
            action='store',
            type=str,
            default='',
            help='file containing MRU list for generated names')
    parser.add_argument('--error-log',
            dest='errorlog',
            action='store',
            type=str,
            default='dognamer.error.log',
            help='error log file (path is relative to *script*)')
    parser.add_argument('-t', '--tweet',
            dest='tweet',
            action='store_true',
            help='post results to twitter')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='print debug spam')
    args = parser.parse_args()

    VERBOSE = args.verbose

    try:
        mrutweets = jltw.mru.MRU()
        if args.mrutweets:
            mrutweets.filename = args.mrutweets
        mrutweets.load()

        mrunames = jltw.mru.MRU()
        if args.mrunames:
            mrunames.filename = args.mrunames
        mrunames.load()

        mark = make_markovator()

        api = None
        if args.numreplies > 0 or args.tweet:
            api = jltw.twapi.open_twitter(args.credentials)

        if args.numreplies > 0:
            make_replies(api, mark, mrutweets, mrunames, args.numreplies, args.numnames, args.delay, args.tweet)
        else:
            make_bare(api, mark, mrunames, args.numnames, args.tweet)

        mrutweets.save()
        mrunames.save()

    except Exception as e:
        import traceback, datetime
        fn = args.errorlog
        if not fn.startswith('/'):
            fn = os.path.join(os.path.dirname(__file__), args.errorlog)
        with open(fn, 'a') as fp:
            fp.write('--------[%s]\n'%str(datetime.datetime.now()))
            fp.write(traceback.format_exc())
            fp.write('\n')
        raise

