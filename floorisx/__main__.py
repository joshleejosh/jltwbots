# floorisx generates games of The Floor Is Lava from shuffled strings.

import argparse, json
import jltw, jltw.grammarizer, jltw.shuffler


# #########################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', type=str, help='File containing grammar data.')
    parser.add_argument('shufffile', type=str, help='File containing token shuffle state.')
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials.')
    parser.add_argument('num_tweets', nargs='?', default=1, type=int, help='Number of sentences to generate.')
    parser.add_argument('-t', '--tweet', dest='tweet', action='store_true', help='Post the result to twitter. If this is set, num_tweets is forced to 1 (to avoid rate errors)')
    args = parser.parse_args()

    fp = open(args.datafile)
    grammar = json.load(fp)
    fp.close()
    shuffler = jltw.shuffler.load(args.shufffile)
    gizer = jltw.grammarizer.Grammarizer(grammar, shuffler)

    api = None
    if args.tweet:
        api = jltw.open_twitter(args.authfile)
        args.num_tweets = 1

    for i in xrange(args.num_tweets):
        s = gizer.generate()
        if args.tweet:
            api.PostUpdate(s)
        jltw.log(s)

    shuffler.save()

