# encoding: utf-8
import os, os.path, codecs
from collections import deque

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_LEN = 48
MRULENTAG = u'^_^MRULEN='

class MRU(object):
    def __init__(self, fn=''):
        self.q = deque([], MRU_LEN)
        self.filename = fn
        self.maxlen = MRU_LEN

    def __str__(self):
        return ' '.join(str(i) for i in self.q)
    def __unicode__(self):
        return u' '.join((unicode(i) for i in self.q))

    def __iter__(self):
        return iter(self.q)

    def __getitem__(self, i):
        return self.q[i]

    def __len__(self):
        return len(self.q)

    def resize(self, newlen):
        self.maxlen = newlen
        self.q = deque(self.q, self.maxlen)

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

            self.maxlen = MRU_LEN
            if len(a)>0 and a[0].startswith(MRULENTAG):
                il = int(a[0][len(MRULENTAG):])
                if il > 0 and il != self.maxlen:
                    self.resize(il)
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
        fp.write(unicode(self.maxlen))
        fp.write(u'\n')
        fp.write(us)
        fp.write(u'\n')
        fp.close()

