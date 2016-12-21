import os, unittest, tempfile, codecs, json
import jltw.shuffler

class ShufflerTest(unittest.TestCase):
    def setUp(self):
        self.tfd, self.tfn = tempfile.mkstemp()
        self.data1 = range(300)
        self.data2 = range(55)
    def tearDown(self):
        os.remove(self.tfn)

    def test_nofile(self):
        # a new shuffler is empty.
        s = jltw.shuffler.Shuffler()
        self.assertEqual(len(s.state), 0)
        buf = []

        # the first request fills and shuffles the state set.
        v = s.choice('test', self.data1)
        self.assertGreater(v, -1)
        self.assertLess(v, 300)
        buf.append(v)
        self.assertEqual(len(s.state), 1)
        self.assertEqual(len(s.state['test']), 299)

        # exhaust the shuffle set.
        # make sure nothing gets repeated along the way.
        for i in xrange(299):
            v = s.choice('test', self.data1)
            self.assertGreater(v, -1)
            self.assertLess(v, 300)
            self.assertNotIn(v, buf)
            buf.append(v)
        self.assertEqual(len(s.state['test']), 0)
        self.assertEqual(sorted(buf), self.data1)

        # the next request triggers a reshuffle.
        v = s.choice('test', self.data1)
        self.assertGreater(v, -1)
        self.assertLess(v, 300)
        self.assertEqual(len(s.state), 1)
        self.assertEqual(len(s.state['test']), 299)

        # calling load or save without a filename should cleanly nop.
        s.load('')
        s.save()

    def test_badfile(self):
        s = jltw.shuffler.Shuffler()
        v = s.choice('test', self.data2)
        ostate = s.state['test']
        s.load(None) # should safely nop and not touch anything.
        self.assertEqual(ostate, s.state['test'])

    def test_persistence(self):
        # load an empty shuffler
        with os.fdopen(self.tfd, 'w') as fp:
            fp.write('{}')
        s = jltw.shuffler.Shuffler()
        s.load(self.tfn)

        # prime it and save it
        v = s.choice('foo', self.data1)
        w = s.choice('bar', self.data2)
        s.save()

        # inspect the json data directly
        with codecs.open(self.tfn, 'r', encoding='utf-8') as fp:
            j = json.load(fp)
            self.assertEqual(len(j), 2)
            self.assertEqual(len(j['foo']), 299)
            self.assertEqual(len(j['foo']), len(set(j['foo']))) # all unique
            self.assertEqual(j['foo'], s.state['foo'])
            self.assertEqual(len(j['bar']), 54)
            self.assertEqual(len(j['bar']), len(set(j['bar'])))
            self.assertEqual(j['bar'], s.state['bar'])

        # reload the file into a new Shuffler instance. All the data should be the same.
        t = jltw.shuffler.Shuffler()
        t.load(self.tfn)
        self.assertEqual(len(s.state), len(t.state))
        self.assertEqual(s.state['foo'], t.state['foo'])
        self.assertEqual(s.state['bar'], t.state['bar'])

        # exhaust the shuffler and make sure it saves correctly.
        for i in xrange(299):
            v = t.choice('foo', self.data1)
        self.assertEqual(len(t.state['foo']), 0)
        for i in xrange(54):
            v = t.choice('bar', self.data2)
        self.assertEqual(len(t.state['bar']), 0)

        t.save()
        with codecs.open(self.tfn, 'r', encoding='utf-8') as fp:
            j = json.load(fp)
            self.assertEqual(len(j), 2)
            self.assertEqual(len(j['foo']), 0)
            self.assertEqual(len(j['bar']), 0)


    # TODO: test edge cases when the base dataset is resized and goes out of sync with the shuffler.

