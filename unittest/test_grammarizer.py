# encoding: utf-8
import os, unittest, tempfile, codecs, collections
import jltw.mru
from jltw.grammarizer import Grammarizer

class MRUTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def _check_distribution(self, ct, sz, t):
        sz = float(sz)
        ratio = float(ct) / sz
        variance = ratio / t - 1.0
        THRESHOLD = 0.2000
        if abs(variance) > THRESHOLD:
            self.fail('Bad Randomness: [%f/%f][%f] -> [%f]'%(ct, sz, ratio, variance))

    def test_empty(self):
        d = { '*': '', }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), '')
        # empty dict will have an empty root added to it
        d = { }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), '')

    def test_badtoken(self):
        d = {
            '*': '{nope}'
        }
        g = Grammarizer(d, None)
        try:
            s = g.generate()
            self.fail('grammarizer should choke on bad token')
        except KeyError:
            pass

    def test_replacement(self):
        d = {
            '*': 'a{foo}f',
            'foo': 'b{bar}e',
            'bar': 'cd',
        }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'abcdef')

    # also tests that keys are lowercased on parse.
    def test_caseify(self):
        d = {
            '*': 'lorem {nochange} ipsum {UPPER} dolor {TItle} amet',
            'nochaNGE': 'AbCd EfGh',
            'upPER': 'iJkL mNoP',
            'tiTLE': 'qrsT uvwX',
        }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem AbCd EfGh ipsum IJKL MNOP dolor Qrst Uvwx amet')

    # this is also a unicode test.
    def test_aan(self):
        d = {
            '*': '{aan} {vowel} {aan} {consonant} {aan} {accvowel} {aan} {accconsonant} {aan} {nonlatin} {aan} {digitstart} {aan} {ystart} {aan} {punctuated}',
            'vowel'        :  'Avowel',
            'consonant'    :  'consonant',
            'accvowel'     : u'âvowel',
            'accconsonant' : u'çonsonant',
            'nonlatin'     : u'እvowel', # \u12A5 ETHIOPIC SYLLABLE GLOTTAL E pronounces as a vowel, but we will fail to recognize it.
            'digitstart'   : u'1owel',
            'ystart'       : u'Ypsilanti', # oh well
            'punctuated'   : u'!?«avowel»',
        }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), u'an Avowel a consonant an âvowel a çonsonant a እvowel a 1owel a Ypsilanti an !?«avowel»')

    def test_squeeze_blank(self):
        d = {
            '*': 'lorem {empty} ipsum',
            'empty': '',
        }
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

        d['*'] = '{empty} lorem ipsum'
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

        d['*'] = 'lorem{empty} ipsum',
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

        d['*'] = 'lorem {empty}ipsum',
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

        d['*'] = 'lorem ipsum {empty}'
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

        d['*'] = 'lorem {empty} {empty} ipsum',
        g = Grammarizer(d, None)
        self.assertEqual(g.generate(), 'lorem ipsum')

    def test_optional(self):
        # A list should give a roughly uniform distribution of its elements.
        d = {
            '*': '{a}',
            'a': ['a', 'b', 'c']
        }
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0}
        for i in xrange(1000):
            c[g.generate()] += 1
        self._check_distribution(c['a'], 1000, 1.0/3.0)
        self._check_distribution(c['b'], 1000, 1.0/3.0)
        self._check_distribution(c['c'], 1000, 1.0/3.0)

        # A '?' in the token adds an empty string to its options, distributed
        # evenly with the rest of the elements.
        d['*'] = '{a?}'
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0, '':0}
        for i in xrange(1000):
            c[g.generate()] += 1
        self._check_distribution(c['a'], 1000, 0.25)
        self._check_distribution(c['b'], 1000, 0.25)
        self._check_distribution(c['c'], 1000, 0.25)
        self._check_distribution(c[''],  1000, 0.25)

        # A '??' in the token makes the token as a whole optional, so the
        # result should come up 50% empty, while the other values evenly split
        # the other 50%.
        d['*'] = '{a??}'
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0, '':0}
        for i in xrange(1000):
            c[g.generate()] += 1
        self._check_distribution(c['a'], 1000, 1.0/6.0)
        self._check_distribution(c['b'], 1000, 1.0/6.0)
        self._check_distribution(c['c'], 1000, 1.0/6.0)
        self._check_distribution(c[''],  1000, 0.5)

    def test_fixed(self):
        d = {
            '*': '{pick},{foo}',
            'foo': '{pick}',
            'pick': ['a', 'b', 'c']
        }
        g = Grammarizer(d, None)
        c = collections.defaultdict(int)
        for i in xrange(9000):
            c[g.generate()] += 1
        self.assertEqual(len(c), 9)
        for k,ct in c.iteritems():
            self._check_distribution(ct, 9000, 1.0/9.0)

        d['*fix'] = ['pick',]
        g = Grammarizer(d, None)
        c = collections.defaultdict(int)
        for i in xrange(9000):
            c[g.generate()] += 1
        self.assertEqual(len(c), 3)
        self._check_distribution(c['a,a'], 9000, 1.0/3.0)
        self._check_distribution(c['b,b'], 9000, 1.0/3.0)
        self._check_distribution(c['c,c'], 9000, 1.0/3.0)

