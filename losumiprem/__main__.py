import argparse
import losumiprem.rhymer

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num-out',
            dest='numout',
            action='store',
            type=int,
            default=1,
            help='number of rhymes to generate')
    parser.add_argument('-m', '--mru-file',
            dest='mrufile',
            action='store',
            default='',
            help='mru list for tracking duplicates')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='count',
            default=0,
            help='more debug spam')
    parser.add_argument('-q', '--quiet',
            dest='quiet',
            action='count',
            default=0,
            help='less debug spam')
    args = parser.parse_args()

    words = [
        'L AO1 R AH0 M',
        'IH1 P S AH0 M',
        'D OW1 L AO0 R',
        'S IH1 T',
        'AH0 M EH1 T',
    ]

    losumiprem.rhymer.set_verbosity(args.verbose - args.quiet)
    for sentence in losumiprem.rhymer.main(words, args.numout, args.mrufile, True):
        sentence = sentence[0].upper() + sentence[1:]
        sentence += '.'
        print sentence

