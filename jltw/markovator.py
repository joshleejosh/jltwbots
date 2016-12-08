import argparse, json, random, xml.sax.saxutils, codecs
from collections import defaultdict, deque

CACHE_DELIM = '\v'
TERMINATOR = '\f'

class Markovator:
    # data is a list of sentences
    # filter is a function(word) that returns True if the word is okay to use, and False if it should be skipped over.
    def __init__(self, data, filter=None, order=2):
        self.cache = defaultdict(list)
        self.corpus = data
        self.order = order
        
        for sentence in self.corpus:
            tokens = deque([TERMINATOR,]*self.order, self.order)
            a = sentence.split()
            for word in a:
                if filter and not filter(word):
                    continue
                self.cache[tuple(tokens)].append(word)
                tokens.append(word)
            self.cache[tuple(tokens)].append(TERMINATOR)

    def chain(self):
        tokens = deque([TERMINATOR,]*self.order, self.order)
        rv = nextword = ''
        while nextword != TERMINATOR:
            nextword = random.choice(list(self.cache[tuple(tokens)]))
            rv += ' ' + nextword
            tokens.append(nextword)
        return rv.strip()

    def generate(self, filter=None, retries=20):
        rv = ''
        faili = 0
        rv = self.chain()
        if filter and retries > 0:
            while not filter(rv) and faili < retries:
                faili += 1
                rv = self.chain()
        return rv



if __name__ == '__main__':
    import argparse, codecs, json, shuffler
    parser = argparse.ArgumentParser()
    parser.add_argument('textfile', type=str, help='File containing one input sentence per line')
    parser.add_argument('num', type=int, nargs='?', default=1, help='Number of sentences to generate')
    args = parser.parse_args()

    fp = codecs.open(args.textfile, encoding='utf-8')
    sentences = fp.readlines()
    fp.close()
    m = Markovator(sentences)
    for i in xrange(args.num):
        print m.generate()
