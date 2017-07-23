# encoding: utf-8
# dognamer replies to tweets with a name for your dog.

import random, time, os.path, codecs
import jltw, jltw.twapi
import markovator
import mrubuddy

VERBOSE = False
DEFAULT_DELAY = 3 # seconds
DEFAULT_NUM_NAMES = 3
DOGNAMES_FN = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'botdata', 'dognames.txt'))
MORDER = 5
RETRIES = 40
PREFIX='Good names for a good dog:\n'

REPLY_WORDS = (
        u'DOG', u'NAME', u'MORE', u'ANOTHER', u'AGAIN',
        )

# ######################################################## #

def read_mentions(api, lastid):
    tweets = api.GetMentions(since_id=lastid, count=100)
    if VERBOSE:
        jltw.log('Found %d mentions'%len(tweets))
    return tweets

def should_reply(tweet):
    # does the tweet contain a picture? (of a dog, presumably)
    if tweet.media:
        return True
    # does the tweet contain the word 'DOG'? (aside from mentioning this bot)
    text = tweet.text.upper().replace('@DOGNAMERBOT', '')
    for w in REPLY_WORDS:
        if text.find(w) != -1:
            return True
    if VERBOSE:
        jltw.log('Do not reply to [%s]'%tweet.text)
    return False

def make_markovator():
    rv = None
    with codecs.open(DOGNAMES_FN, encoding='utf-8') as fp:
        # read the data file: one item per line, each line split
        # into a list of letters (rather than words)
        data = [list(s.strip()) for s in fp.readlines()]
        rv = markovator.Markovator(data, order=MORDER, verbose=False)
    return rv

def make_body(mark, mrunames, numnames):
    def ffilter(w):
        w = u''.join(w)
        u = w.upper()
        for n in mark.corpus:
            n = u''.join(n).upper()
            if n.find(u) != -1:
                return False
        if w in mrunames:
            return False
        return True

    names = []
    for _ in range(numnames):
        n = mark.generate(filter=ffilter, retries=RETRIES)
        n = u''.join(n)
        names.append(n)
        mrunames.add(n)
    text = PREFIX
    text += u'\n'.join(['%d. %s'%(i+1,n) for i,n in enumerate(names)])
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

            if VERBOSE:
                jltw.log('Reply to [%s]'%mention.text)
            body = make_body(mark, mrunames, numnames)
            body = u'@%s %s'%(mention.user.screen_name, body)
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
    import argparse, codecs, json, traceback, datetime
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
            default=DEFAULT_NUM_NAMES,
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
        mrutweets = mrubuddy.MRU()
        if args.mrutweets:
            mrutweets.filename = args.mrutweets
        mrutweets.load()

        mrunames = mrubuddy.MRU()
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
        fn = args.errorlog
        if not fn.startswith('/'):
            fn = os.path.join(os.path.dirname(__file__), args.errorlog)
        with open(fn, 'a') as fp:
            fp.write('--------[%s]\n'%str(datetime.datetime.now()))
            fp.write(traceback.format_exc())
            fp.write('\n')
        raise

