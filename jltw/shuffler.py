# encoding: utf-8
# Persist shuffled sequences across runs of a program.

import os.path, json, random, codecs
import jltw

class Shuffler:
    def __init__(self):
        self.filename = ''
        self.state = {}
        self.rng = random.Random()

    def load(self, fn):
        self.filename = fn
        if not self.filename:
            return
        if not os.path.exists(self.filename):
            return
        with codecs.open(self.filename, encoding='utf-8') as fp:
            self.state = json.load(fp)

    def save(self, fn=None):
        if fn:
            self.filename = fn
        if not self.filename:
            return
        with codecs.open(self.filename, 'w', encoding='utf-8') as fp:
            s = json.dumps(self.state, fp, ensure_ascii=False)
            s = s.replace('{', '{\n')
            s = s.replace('}', '\n}')
            s = s.replace('], ', '],\n')
            fp.write(s)

    def choice(self, k, a):
        # load or reload this key into state
        if k in self.state and len(self.state[k]) > 0:
            pass
        else:
            self._refresh(k, a)

        # pick off the first element from this key's shuffled array
        v = -1
        if k in self.state and len(self.state[k]) > 0:
            v = self.state[k].pop(0)

        rv = u''
        if v > -1:
            if v < len(a):
                rv = a[v]
            else:
                #jltw.log('fail: not enough elements for %d in %s (%d: [%s])'%(i, k, len(a), a))
                rv = self.rng.choice(a)
        else:
            #jltw.log(u'¯\_(ツ)_/¯')
            rv = self.rng.choice(a)
        return rv

    def _refresh(self, k, a):
        #jltw.log('refresh %s'%k)
        sa = list(range(len(a)))
        self.rng.shuffle(sa)
        self.state[k] = sa


if __name__ == '__main__':
    import unittest, tempfile
    class ShufflerTest(unittest.TestCase):
        def setUp(self):
            self.fd, self.fn = tempfile.mkstemp()
            with open(self.fn, 'w') as fp:
                fp.write('{}')
        def tearDown(self):
            try:
                os.close(self.fd)
            except OSError:
                pass
            try:
                os.remove(self.fn)
            except OSError:
                pass

        def test_basic(self):
            k = '  fOo  '
            a = ['b', -1, 'Q', 4.342]
            s = Shuffler()
            o1 = []
            o1.append(s.choice(k, a))
            self.assertIn(k, s.state)
            self.assertEqual(len(s.state[k]), 3) # first item has already been popped off
            self.assertNotIn(o1[0], s.state[k])
            o1.append(s.choice(k, a))
            o1.append(s.choice(k, a))
            o1.append(s.choice(k, a))
            self.assertEqual(len(s.state[k]), 0)
            self.assertItemsEqual(a, o1)
            o2 = []
            o2.append(s.choice(k, a))
            o2.append(s.choice(k, a))
            o2.append(s.choice(k, a))
            o2.append(s.choice(k, a))
            self.assertItemsEqual(a, o2)

        def test_file(self):
            s = Shuffler()
            s.rng = random.Random(91867967548)
            s.load(self.fn)
            a = [-452.611, 97, 6.28]
            b = ['You', 'mE', '  they  ', 'WE', 'us']
            self.assertEqual(s.choice('j', a), a[0])
            self.assertEqual(s.choice('k', b), b[4])
            s.save()
            with open(self.fn) as fp:
                j = json.load(fp)
                self.assertEqual(j['j'], [2, 1])
                self.assertEqual(j['k'], [3, 2, 0, 1])

            t = Shuffler()
            t.load(self.fn)
            self.assertEqual(t.choice('j', a), a[2])
            self.assertEqual(t.choice('k', b), b[3])
            t.save()
            with open(self.fn) as fp:
                j = json.load(fp)
                self.assertEqual(j['j'], [1])
                self.assertEqual(j['k'], [2, 0, 1])

    unittest.main(verbosity=2)

