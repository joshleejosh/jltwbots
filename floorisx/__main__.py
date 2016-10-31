# floorisx generates games of The Floor Is Lava from shuffled strings.

import argparse, json, random, re
import jltw, shuffler

GRAMMAR={}
SHUFFLER=None

# #########################################################

def load_grammar(fn):
    global GRAMMAR
    fp = open(fn)
    GRAMMAR = json.load(fp)
    fp.close()
    return GRAMMAR

def load_shuffler(fn):
    global SHUFFLER
    SHUFFLER = shuffler.load(fn)
    return SHUFFLER

# #########################################################

RE_TOKEN=re.compile(r'{([^}]*)}')

def replace_tokens(key, ins):
    if isinstance(ins, basestring):
        match = RE_TOKEN.search(ins)
        while match:
            mkey = match.group(1).strip()
            repl = replace_tokens(mkey, GRAMMAR[mkey])
            ins = ins.replace('{%s}'%mkey, repl)
            match = RE_TOKEN.search(ins)

        # HACK: a/an replacement
        if key == 'destsingular' and ins[0:2].lower() == 'a ':
            if ins[2].lower() in ('a', 'e', 'i', 'o', 'u'):
                ins = 'an ' + ins[2:]

        return ins
    elif hasattr(ins, '__iter__'):
        v = SHUFFLER.choice(key, ins)
        return replace_tokens(key, v)
    else:
        return ins

def spew():
    rv = replace_tokens('*', GRAMMAR['*'])
    return rv


# #########################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', type=str, help='File containing grammar data.')
    parser.add_argument('shufffile', type=str, help='File containing token shuffle state.')
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials.')
    parser.add_argument('num_tweets', nargs='?', default=1, type=int, help='Number of sentences to generate.')
    parser.add_argument('-t', '--tweet', dest='tweet', action='store_true', help='Post the result to twitter. If this is set, num_tweets is forced to 1 (to avoid rate errors)')
    args = parser.parse_args()

    load_grammar(args.datafile)
    load_shuffler(args.shufffile)

    api = None
    if args.tweet:
        api = jltw.open_twitter(args.authfile)
        args.num_tweets = 1

    for i in xrange(args.num_tweets):
        s = spew()
        if args.tweet:
            api.PostUpdate(s)
        print s.decode('utf-8')

    SHUFFLER.save()

