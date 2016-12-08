import argparse, json, random, xml.sax.saxutils, codecs
from collections import defaultdict

MAX_FILTER_FAILURES = 20
CACHE_DELIM = '\v'
TERMINATOR = '\f'

class Markovator:
    # data is a list of sentences
    # filter is a function(word) that returns True if the word is okay to use, and False if it should be skipped over.
    def __init__(self, data, filter=None):
        self.cache = defaultdict(list)
        self.corpus = data
        
        for sentence in self.corpus:
            p = q = TERMINATOR
            a = sentence.split()
            for word in a:
                word = word.strip()
                if not word:
                    continue
                if filter and not filter(word):
                    continue
                try:
                    self.cache[(p,q)].append(word)
                except KeyError:
                    self.cache[(p,q)] = [word]
                p = q
                q = word
            self.cache[(p,q)].append(TERMINATOR)

    def chain(self):
        p = q = TERMINATOR
        rv = nextword = ''
        while nextword != TERMINATOR:
            nextword = random.choice(list(self.cache[(p,q)]))
            rv += ' ' + nextword
            p = q
            q = nextword
        return rv.strip()

    def generate(self, filter=None):
        rv = ''
        faili = 0
        rv = self.chain()
        if filter:
            while not filter(rv) and faili < MAX_FILTER_FAILURES:
                faili += 1
                #print '!REJECTED: %s'%rv
                rv = self.chain()
        return rv



if __name__ == '__main__':
    import argparse, codecs, json, shuffler
    parser = argparse.ArgumentParser()
    parser.add_argument('textfile', type=str)
    parser.add_argument('num', type=int, nargs='?', default=1)
    args = parser.parse_args()

    fp = codecs.open(args.textfile, encoding='utf-8')
    sentences = fp.readlines()
    fp.close()
    m = Markovator(sentences)
    for i in xrange(args.num):
        print m.generate()

