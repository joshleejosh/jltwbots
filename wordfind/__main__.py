# encoding: utf-8
import argparse, time
import jltw
import wordfind, formatter

def _html_test(words, solution, filled):
    tweet = formatter.format_text(words, filled, replace=True)
    jltw.log(tweet)
    solved = formatter.format_solution(words, solution, filled)
    jltw.log(solved)
    import codecs
    with codecs.open('wordfind_test.html','w', encoding='utf-8') as fp:
        fp.write('<html><pre style="font-size:2em;">')
        fp.write(tweet)
        fp.write('\n')
        fp.write(solved)
        fp.write('</pre></html>')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('wordlist')
    parser.add_argument('-t', '--tweet',
            dest='tweet',
            action='store',
            type=str,
            default='',
            help='post to twitter, with credentials in given file.')
    parser.add_argument('-s', '--seed',
            dest='seed',
            action='store',
            type=int,
            default=int(time.time()),
            help='seed value for randomizer')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='print debug spam')
    args = parser.parse_args()

    wordfind.set_verbose(args.verbose)
    wordfind.set_seed(args.seed)
    wordfind.load_wordlists(args.wordlist)
    jltw.log('Seed [%d]'%args.seed)

    api = None
    if args.tweet:
        api = jltw.open_twitter(args.tweet)

    words, solution, filled = wordfind.make_grid()
    text = formatter.format_text(words, solution, filled)
    jltw.log(text)
    #_html_test(words, solution, filled)

    if args.tweet:
        tweet = formatter.format_text(words, filled, replace=True)
        api.PostUpdate(tweet, verify_status_length=False)

