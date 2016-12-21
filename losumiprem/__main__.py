import os, json, codecs, argparse, random
from losumiprem.rhymer import set_verbosity, find_rhymes
from losumiprem.filters import in_names, is_wordnet_proper

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('grammarfile',
            help='output grammar file')
    parser.add_argument('-n', '--num-out',
            dest='numout',
            action='store',
            type=int,
            default=1,
            help='number of rhymes to generate')
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

    words = [
        u'L AO1 R AH0 M',
        u'IH1 P S AH0 M',
        u'D OW1 L AO0 R',
        u'S IH1 T',
        u'AH0 M EH1 T',
    ]

    rhymes = []
    for i in xrange(len(words)):
        a = find_rhymes(words[i], isarpabetized=True)
        a = [w.title() if in_names(w) or is_wordnet_proper(w) else w for w in a]
        rhymes.append(a)

    grammar = {
        '*': '{Lorem} {ipsum} {dolor} {sit} {amet}.',
        'lorem': rhymes[0],
        'ipsum': rhymes[1],
        'dolor': rhymes[2],
        'sit': rhymes[3],
        'amet': rhymes[4],
    }
    args.grammarfile = os.path.realpath(args.grammarfile)
    with codecs.open(args.grammarfile, 'w', encoding='utf-8') as fp:
        json.dump(grammar, fp, indent=1)

