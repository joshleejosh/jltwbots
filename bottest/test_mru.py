# encoding: utf-8
import os, unittest, tempfile, codecs
import jltw.mru

class MRUTest(unittest.TestCase):
    def setUp(self):
        self.tfd, self.tfn = tempfile.mkstemp()
        self.data = [u'ä', 'b', u'ç', 'd', 'e', 'f']
    def tearDown(self):
        os.remove(self.tfn)

    def test_nofile(self):
        m = jltw.mru.MRU()
        self.assertEqual(m.maxlen, jltw.mru.MRU_LEN)
        self.assertEqual(m.q.maxlen, m.maxlen)
        m.load() # should safely nop
        for c in self.data:
            m.add(c)
        m.save('g') # should add the element, then safely nop
        self.assertEqual(len(m), 7)
        self.assertEqual(unicode(m), u'ä b ç d e f g')

    def test_in(self):
        m = jltw.mru.MRU()
        for c in self.data:
            m.add(c)
        self.assertIn(u'ç', m)
        self.assertIn(u'f', m)
        self.assertNotIn(u'c', m)

    def test_iter(self):
        m = jltw.mru.MRU()
        for c in self.data:
            m.add(c)
        for i,c in enumerate(m):
            self.assertEqual(c, self.data[i])

    def test_resize(self):
        m = jltw.mru.MRU()
        for c in self.data:
            m.add(c)
        self.assertEqual(unicode(m), u'ä b ç d e f')
        m.resize(3)
        self.assertEqual(unicode(m), u'd e f')

    def test_load_save_unicode(self):
        with codecs.open(self.tfn, 'w', encoding='utf-8') as fp:
            us = u'%s7\nmmm\nñññ\nó�ó\nppp\nqqq'%jltw.mru.MRULENTAG
            fp.write(us)
        m = jltw.mru.MRU(self.tfn)
        m.load()
        self.assertEqual(m.maxlen, 7)
        self.assertEqual(len(m), 5)
        self.assertEqual(unicode(m), u'mmm ñññ ó�ó ppp qqq')
        m.add('r')
        m.add(u'ß')
        m.add(u'𐂜')
        self.assertEqual(unicode(m), u'ñññ ó�ó ppp qqq r ß 𐂜')
        m.save()
        with codecs.open(self.tfn, encoding='utf-8') as fp:
            ut = u'%s7\nñññ\nó�ó\nppp\nqqq\nr\nß\n𐂜\n'%jltw.mru.MRULENTAG
            self.assertEqual(fp.read(), ut)

    def test_save(self):
        # Load the empty file
        m = jltw.mru.MRU(self.tfn)
        m.load()
        self.assertEqual(m.maxlen, jltw.mru.MRU_LEN)
        self.assertEqual(len(m), 0)

        # Resize and load up
        m.resize(4)
        for c in self.data:
            m.add(c)
        self.assertEqual(unicode(m), u'ç d e f')

        # Save it and check the file contents
        m.save()
        with codecs.open(self.tfn, 'r', encoding='utf-8') as fp:
            s = fp.read()
            self.assertEqual(s, u'%s4\nç\nd\ne\nf\n'%jltw.mru.MRULENTAG)

        # Load a new instance and check state
        n = jltw.mru.MRU(self.tfn)
        n.load()
        self.assertEqual(n.maxlen, 4)
        self.assertEqual(len(n), 4)
        self.assertEqual(unicode(n), u'ç d e f')


