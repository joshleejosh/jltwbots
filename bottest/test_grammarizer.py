# encoding: utf-8
import os, unittest, tempfile, codecs, collections
import numpy, math
import jltw
from jltw.grammarizer import Grammarizer

class GrammarizerTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def _check_distribution(self, ct, sz, pr):
        if pr == 0:
            if ct != 0:
                self.fail('Bad Randomness: [%f] -> [%f]'%(pr, ct))
            return
        rate = float(ct) / float(sz)
        variance = rate / pr - 1.0
        THRESHOLD = 0.1000
        if abs(variance) > THRESHOLD:
            self.fail('Bad Randomness: [%f/%f][%f] -> [%f]'%(ct, sz, rate, variance))

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
        except:
            raise

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
        sampsz = 9000
        # A list should give a roughly uniform distribution of its elements.
        d = {
            '*': '{q}',
            'q': ['a', 'b', 'c']
        }
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0}
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self._check_distribution(c['a'], sampsz, 1.0/3.0)
        self._check_distribution(c['b'], sampsz, 1.0/3.0)
        self._check_distribution(c['c'], sampsz, 1.0/3.0)

        # A '?' in the token adds an empty string to its options, distributed
        # evenly with the rest of the elements.
        d['*'] = '{q?}'
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0, '':0}
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self._check_distribution(c['a'], sampsz, 0.25)
        self._check_distribution(c['b'], sampsz, 0.25)
        self._check_distribution(c['c'], sampsz, 0.25)
        self._check_distribution(c[''],  sampsz, 0.25)

        # A '??' in the token makes the token as a whole optional, so the
        # result should come up 50% empty, while the other values evenly split
        # the other 50%.
        d['*'] = '{q??}'
        g = Grammarizer(d, None)
        c = {'a':0, 'b':0, 'c':0, '':0}
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self._check_distribution(c['a'], sampsz, 1.0/6.0)
        self._check_distribution(c['b'], sampsz, 1.0/6.0)
        self._check_distribution(c['c'], sampsz, 1.0/6.0)
        self._check_distribution(c[''],  sampsz, 0.5)

    def test_weighted(self):
        sampsz = 9000
        d = {
            '*': '{q}',
            'q': [
                '{r*3}', # this counts as 3 r's
                '{s}',
                'qq{t*100}', # the extra text means this won't be parsed as a weight.
                '{u*0}', # this will never be picked
                '{v*2}'
            ],
            'r': 'a',
            's': 'b{v*10}', # a weight in a string has no effect
            't*100': 'c',
            'u': 'd',
            'v': 'e',
            'v*10': 'f'
        }
        g = Grammarizer(d, None)
        c = {'a':0, 'bf':0, 'qqc':0, 'd':0, 'e':0}
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self._check_distribution(c['a'],   sampsz, 3.0/7.0)
        self._check_distribution(c['bf'],  sampsz, 1.0/7.0)
        self._check_distribution(c['qqc'], sampsz, 1.0/7.0)
        self._check_distribution(c['d'],   sampsz, 0.0/7.0)
        self._check_distribution(c['e'],   sampsz, 2.0/7.0)

    def test_fixed(self):
        sampsz = 9000
        d = {
            '*': '{pick},{foo}',
            'foo': '{pick}',
            'pick': ['a', 'b', 'c']
        }
        g = Grammarizer(d, None)
        c = collections.defaultdict(int)
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self.assertEqual(len(c), 9)
        for k,ct in c.iteritems():
            self._check_distribution(ct, sampsz, 1.0/9.0)

        d['*fix'] = ['pick',]
        g = Grammarizer(d, None)
        c = collections.defaultdict(int)
        for i in xrange(sampsz):
            c[g.generate()] += 1
        self.assertEqual(len(c), 3)
        self._check_distribution(c['a,a'], sampsz, 1.0/3.0)
        self._check_distribution(c['b,b'], sampsz, 1.0/3.0)
        self._check_distribution(c['c,c'], sampsz, 1.0/3.0)

