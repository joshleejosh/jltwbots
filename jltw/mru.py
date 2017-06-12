# encoding: utf-8
import sys, os, os.path, codecs
from collections import deque

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_LEN = 48
MRULENTAG = u'^_^MRULEN='

def u(i):
    if sys.version_info >= (3,0):
        return str(i)
    return unicode(i)

class MRU(object):
    def __init__(self, fn=''):
        self.q = deque([], MRU_LEN)
        self.filename = fn
        self.maxlen = MRU_LEN

    def __str__(self):
        return ' '.join(str(i) for i in self.q)
    def __unicode__(self):
        return u' '.join((u(i) for i in self.q))

    def __iter__(self):
        return iter(self.q)

    def __getitem__(self, i):
        return self.q[i]

    def __len__(self):
        return len(self.q)

    def resize(self, newlen):
        if newlen == self.maxlen:
            return
        if newlen < 1:
            return
        self.maxlen = newlen
        self.q = deque(self.q, self.maxlen)

    def add(self, v):
        if v:
            self.q.append(v)

    def serialize(self):
        rv = u'%s%d\n'%(MRULENTAG, self.maxlen)
        us = u'\n'.join((u(i) for i in self.q))
        rv = rv + us + '\n'
        return rv

    def deserialize(self, s):
        a = s.split('\n')
        self.maxlen = MRU_LEN
        if len(a)>0 and a[0].startswith(MRULENTAG):
            il = int(a[0][len(MRULENTAG):])
            if il > 0:
                self.resize(il)
            del a[0]
        for i in a:
            self.add(i)

    def load(self):
        if not self.filename:
            return
        if os.path.exists(self.filename):
            with codecs.open(self.filename, encoding='utf-8') as fp:
                self.deserialize(fp.read())
        else:
            with codecs.open(self.filename, 'w', encoding='utf-8'):
                fp.write('')

    def save(self, newid=None):
        if newid:
            self.add(newid)
        if not self.filename:
            return
        s = self.serialize()
        with codecs.open(self.filename, 'w', encoding='utf-8') as fp:
            fp.write(s)

if __name__ == '__main__':
    import unittest, tempfile
    class MRUTest(unittest.TestCase):
        def setUp(self):
            self.fd, self.fn = tempfile.mkstemp()
        def tearDown(self):
            try:
                os.close(self.fd)
            except OSError:
                pass
            try:
                os.remove(self.fn)
            except OSError:
                pass

        def test_mru(self):
            m = MRU()
            self.assertEqual(m.maxlen, MRU_LEN)
            self.assertEqual(str(m), '')
            m.add(3)
            m.add('Q')
            self.assertIn(3, m)
            self.assertIn('Q', m)
            self.assertNotIn('R', m)
            self.assertEqual(m.serialize(), u'^_^MRULEN=48\n3\nQ\n')

        def test_maxlen(self):
            m = MRU()
            self.assertEqual(m.maxlen, MRU_LEN)
            m.resize(4)
            self.assertEqual(m.maxlen, 4)
            for i in range(10):
                m.add(i)
            self.assertNotIn(0, m)
            self.assertNotIn(5, m)
            self.assertIn(6, m)
            self.assertIn(7, m)
            self.assertIn(8, m)
            self.assertIn(9, m)
            self.assertEqual(m.serialize(), u'^_^MRULEN=4\n6\n7\n8\n9\n')

            # resize up
            m.resize(6)
            self.assertEqual(m.serialize(), u'^_^MRULEN=6\n6\n7\n8\n9\n')

            # resizing down lops off the head
            m.resize(2)
            self.assertEqual(m.serialize(), u'^_^MRULEN=2\n8\n9\n')

            # can't resize to 0
            m.resize(0)
            self.assertEqual(m.serialize(), u'^_^MRULEN=2\n8\n9\n')

        def test_file(self):
            m = MRU(self.fn)
            self.assertTrue(os.path.exists(self.fn))
            self.assertEqual(os.path.getsize(self.fn), 0)
            m.resize(4)

            m.add('hi there')
            m.add(32.6)
            m.add(14)
            m.save()
            with open(self.fn) as fp:
                s = fp.read()
            self.assertEqual(s, m.serialize())

            m.add(89576)
            m.add('whatever')
            m.save(62.73)
            with open(self.fn) as fp:
                s = fp.read()
            self.assertEqual(s, m.serialize())
            self.assertEqual(s, u'^_^MRULEN=4\n14\n89576\nwhatever\n62.73\n')

            n = MRU(self.fn)
            n.load()
            self.assertEqual(n.serialize(), u'^_^MRULEN=4\n14\n89576\nwhatever\n62.73\n')

    unittest.main(verbosity=2)

