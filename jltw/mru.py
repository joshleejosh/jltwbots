# encoding: utf-8
import os, os.path, codecs
from collections import defaultdict, deque

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_LEN = 48
MRULENTAG = u'^_^MRULEN='

class MRU(object):
    def __init__(self, fn=''):
        self.q = deque([], MRU_LEN)
        self.filename = fn
        self.length = MRU_LEN

    def __str__(self):
        return ' '.join(str(i) for i in self.q)
    def __unicode__(self):
        return u' '.join((unicode(i) for i in self.q))

    def __iter__(self):
        return iter(self.q)
    
    def __getitem__(self, i):
        return self.q[i]

    def add(self, v):
        if v:
            self.q.append(v)

    def load(self):
        if not self.filename:
            return
        if os.path.exists(self.filename):
            fp = codecs.open(self.filename, encoding='utf-8')
            a = fp.read().split('\n')
            fp.close()

            self.length = MRU_LEN
            if len(a)>0 and a[0].startswith(MRULENTAG):
                il = int(a[0][len(MRULENTAG):])
                if il > 0 and il != self.length:
                    self.length = il
                    self.q = deque(self.q, self.length)
                del a[0]

            for i in a:
                self.add(i)
        else:
            fp = codecs.open(self.filename, 'w', encoding='utf-8')
            fp.close()

    def save(self, newid=None):
        if newid:
            self.add(newid)
        if not self.filename:
            return
        us = '\n'.join((unicode(i) for i in self.q))

        fp = codecs.open(self.filename, 'w', encoding='utf-8')
        fp.write(MRULENTAG)
        fp.write(unicode(self.length))
        fp.write(u'\n')
        fp.write(us)
        fp.write(u'\n')
        fp.close()

if __name__ == '__main__':
    import tempfile
    print '1: Build an MRU from scratch'
    tfd, tfn = tempfile.mkstemp()
    try:
        m = MRU(tfn)
        m.load()
        m.add('a')
        m.add('b')
        m.add('c')
        m.add('d')
        m.add('e')
        print 'd' in m
        print 'f' in m
        print m
        m.save()
        with open(tfn) as fp:
            print fp.read()
        m.add('f')
        m.add('g')
        m.add('h')
        m.save()
        with open(tfn) as fp:
            print fp.read()
    finally:
        os.remove(tfn)

    print '2: Check/add to an existing MRU file, adjust size'
    tfd, tfn = tempfile.mkstemp()
    try:
        os.write(tfd, MRULENTAG+'4\nz\ny\nx\n')
        with open(tfn) as fp:
            print fp.read()
        m = MRU(tfn)
        print m.q.maxlen
        m.load()
        print m.q.maxlen
        print ' '.join(m)
        m.add('a')
        m.add('b')
        m.add('c')
        print [i.upper() for i in m]
        m.save()
        with open(tfn) as fp:
            print fp.read()
    finally:
        os.remove(tfn)

    print '3: Do a file-less temp MRU'
    m = MRU()
    print m.q.maxlen
    m.load() # should safely nop
    print m
    m.add(u'ä')
    m.add(u'b')
    m.add(u'ç')
    m.save(u'd') # should safely nop (aside from the add)
    try:
        print str(m)
    except Exception as e:
        print e
    try:
        print unicode(m)
    except Exception as e:
        print e

