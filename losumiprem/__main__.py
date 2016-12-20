import argparse, random
import jltw.mru
from losumiprem.rhymer import set_verbosity, find_rhymes
from losumiprem.filters import in_names, is_wordnet_proper

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

    set_verbosity(args.verbose - args.quiet)
    mru = jltw.mru.MRU(args.mrufile)
    mru.load()

    words = [
        'L AO1 R AH0 M',
        'IH1 P S AH0 M',
        'D OW1 L AO0 R',
        'S IH1 T',
        'AH0 M EH1 T',
    ]

    rhymes = []
    for i in xrange(len(words)):
        a = find_rhymes(words[i], isarpabetized=True)
        a = [w.title() if in_names(w) or is_wordnet_proper(w) else w for w in a]
        rhymes.append(a)

    for i in xrange(args.numout):
        s = ''
        while not s or s in mru:
            s = ' '.join((random.choice(w) for w in rhymes))
            s = s[0].upper() + s[1:]
            s += '.'
        print s
        mru.add(s)

    mru.save()

