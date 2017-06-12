# encoding: utf-8
import random, time
import jltw, jltw.twapi, jltw.shuffler, jltw.mru, jltw.grammarizer

VERBOSE = False
SEARCH_STRING = 'mic drop'
DEFAULT_DELAY = 10 # seconds

# ######################################################## #

GRAMMAR = {
    "*": "[{Pickup}{conjunction}{action}]",

    "pickup": [
        "takes the mic off the ground",
        "picks the mic back up",
        "picks up the mic",
        "catches the mic",
        "grabs the mic",
        "finds the mic",
        "retrieves the mic",
        "scrambles for the mic",
    ],

    "conjunction": [
        " and ", ", ", "; ",
        " and ", ", ", "; ",
    ],

    "action": [
        "makes sure it isn't damaged",
        "examines it curiously",
        "checks it for dents",
        "cleans it off",
        "dusts it off",
        "checks the connection",
        "plugs it back in",
        "sets it back in its stand",
        "carries it offstage",
        "replaces it with a fresh one",
        "wipes it down with a handkerchief",
        #"throws it off the stage",
        #"whips it around by its cord",
        #"tosses it into the trash",
        #"whispers comforting words to it",
    ],
}

# ######################################################## #

def find_micdrops(api, lastid):
    tweets = api.GetSearch(term=SEARCH_STRING,
            result_type='recent',
            since_id=lastid,
            count=100)
    tweets = [t for t in tweets if not t.retweeted_status]
    #         and not t.in_reply_to_status_id]
    if VERBOSE:
        jltw.log('found', len(tweets))
    return tweets

def make_reply(tweet, grammar):
    if VERBOSE:
        jltw.log('----')
        jltw.log(tweet.id_str)
        jltw.log(tweet.created_at)
        jltw.log(tweet.user.screen_name)
        jltw.log(tweet.text)
    rv = '@' + tweet.user.screen_name + ' ' + grammar.generate()
    return rv

def micassist_main(credentials, grammarizer, shuffler, mru, numreplies, delay, alsobare, dotweet):
    lastid = None
    if len(mru) > 0:
        lastid = mru[-1]

    api = jltw.twapi.open_twitter(credentials)

    if numreplies > 0:
        drops = find_micdrops(api, lastid)
        ndrops = len(drops)

        if len(drops) == 0:
            if VERBOSE:
                jltw.log(u'no tweets found to reply to')

        else:
            ntweets = 0
            while ntweets < numreplies and len(drops) > 0:
                drop = random.choice(drops)
                drops.remove(drop)
                if drop.id_str in mru:
                    continue
                mru.add(drop.id_str)
                line = make_reply(drop, gizer)
                jltw.log(line)
                if dotweet:
                    api.PostUpdate(line, in_reply_to_status_id=drop.id_str)
                ntweets += 1
                time.sleep(delay)

            if VERBOSE:
                jltw.log('----')
                if ntweets < numreplies:
                    jltw.log('Exhausted tweets at %d/%d'%(ntweets, numreplies))
                else:
                    jltw.log('Replied to %d/%d'%(ntweets, ndrops))

    bchance = random.random()
    if VERBOSE:
        jltw.log(bchance)
    if bchance < alsobare:
        line = grammarizer.generate()
        jltw.log(line)
        if dotweet:
            api.PostUpdate(line)

# ######################################################## #

if __name__ == '__main__':
    import argparse, codecs, json
    parser = argparse.ArgumentParser()
    parser.add_argument('credentials',
            type=str,
            help='file containing twitter credentials')
    parser.add_argument('-m', '--mrufile',
            dest='mrufile',
            action='store',
            default='',
            help='file containing MRU list for tweets replied to')
    parser.add_argument('-s', '--shufflefile',
            dest='shuffile',
            action='store',
            default='',
            help='file containing grammar shuffle state')
    parser.add_argument('-n', '--num-replies',
            dest='numreplies',
            action='store',
            type=int,
            default=1,
            help='number of tweets to find and reply to')
    parser.add_argument('-d', '--delay',
            dest='delay',
            action='store',
            type=int,
            default=DEFAULT_DELAY,
            help='time between tweets')
    parser.add_argument('-b', '--barechance',
            dest='bare',
            action='store',
            type=float,
            default=0,
            help='odds of also posting a non-reply tweet')
    parser.add_argument('-t', '--tweet',
            dest='tweet',
            action='store_true',
            help='post results to twitter')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='print debug spam')
    parser.add_argument('-g', '--grammar-test',
            dest='grammar_test',
            action='store_true',
            help='just test the grammar')
    args = parser.parse_args()

    VERBOSE = args.verbose

    mru = jltw.mru.MRU()
    if args.mrufile:
        mru.filename = args.mrufile
    mru.load()

    shuffler = jltw.shuffler.Shuffler()
    if args.shuffile:
        shuffler.load(args.shuffile)

    gizer = jltw.grammarizer.Grammarizer(GRAMMAR, shuffler)
    gizer.verbose = args.verbose

    if args.grammar_test:
        for _ in xrange(args.numreplies):
            print gizer.generate()
    else:
        micassist_main(args.credentials, gizer, shuffler, mru, args.numreplies, args.delay, args.bare, args.tweet)

    shuffler.save()
    mru.save()

