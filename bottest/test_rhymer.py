# encoding: utf-8
import os, unittest
import losumiprem.rhymer
import nltk
from nltk.corpus import cmudict

class RhymerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CWD = os.path.realpath(os.path.dirname(__file__))
        nltk.data.path.insert(0, os.path.join(CWD, 'botenv', 'nltk_data'))
        cls.pdict = cmudict.dict()
    @classmethod
    def tearDownClass(cls):
        cls.pdict = cmudict.dict()

    def test_perfect_rhyme(self):
        s = RhymerTest.pdict['greedier'][0]
        t = RhymerTest.pdict['speedier'][0]
        self.assertTrue(losumiprem.rhymer.perfect_rhyme(s, t))

        s = RhymerTest.pdict['op'][0]
        t = RhymerTest.pdict['flop'][0]
        self.assertTrue(losumiprem.rhymer.perfect_rhyme(s, t))

        # stresses are inconsistent, but they align
        s = RhymerTest.pdict['rumour'][0]
        t = RhymerTest.pdict['tumor'][0]
        self.assertTrue(losumiprem.rhymer.perfect_rhyme(s, t))

        # stresses align, vowels match, but the intervening consonant doesn't
        s = RhymerTest.pdict['meaty'][0]
        t = RhymerTest.pdict['beefy'][0]
        self.assertFalse(losumiprem.rhymer.perfect_rhyme(s, t))

        # should fail: bar/bar is imperfect
        s = RhymerTest.pdict['rebar'][0]
        t = RhymerTest.pdict['disbar'][0]
        self.assertFalse(losumiprem.rhymer.perfect_rhyme(s, t))

        # multiple instances of the primary stress marker; count forward from the last one, match
        s = RhymerTest.pdict['raphaela'][0]
        t = RhymerTest.pdict['rubella'][0]
        self.assertTrue(losumiprem.rhymer.perfect_rhyme(s, t))

        # stresses align, phonemes match, but length is uneven
        s = RhymerTest.pdict['mare'][0]
        t = RhymerTest.pdict['berry'][0]
        self.assertFalse(losumiprem.rhymer.perfect_rhyme(s, t))

    def test_levenshtein(self):
        s = []
        t = []
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 0)
        s = [1, 2, 3, 4, 5, 6]
        t = [1, 3, 4, 5, 6]
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)
        s = ['one', 'two', 'three', 'four']
        t = ['lorem', 'two', 'ipsum']
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 3)

        s = 'funk'
        t = 'funk'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 0)

        # insertion, deletion
        s = 'funk'
        t = 'fun'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)
        s = 'fun'
        t = 'funk'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)
        s = 'unk'
        t = 'funk'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)
        s = 'funk'
        t = 'n'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 3)

        # substitution
        s = 'funk'
        t = 'junk'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)
        s = 'fink'
        t = 'funk'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 1)

        # mix
        s = 'funk'
        t = 'afadf'
        self.assertEqual(losumiprem.rhymer.levenshtein(s, t), 4)


