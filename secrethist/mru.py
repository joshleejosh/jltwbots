import os.path, codecs
from collections import defaultdict

WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_LEN = 48
MRULENTAG = u'^_^MRULEN='

class MRU:
    def __init__(self):
        self.values = []
        self.length = MRU_LEN
    def __str__(self):
        return '%d/%d: [%s]'%(len(self.values), self.length, ', '.join(self.values).encode('utf-8'))
    def __unicode__(self):
        return u'%d/%d: [%s]'%(len(self.values), self.length, u', '.join(self.values))
    def isin(self, v):
        return (v in self.values)
    def add(self, v):
        if v in self.values:
            return
        self.values.append(v)
        while len(self.values) > self.length:
            del self.values[0]

mrus = defaultdict(MRU)

def load_mru(n):
    fn = os.path.join(WDIR, n+'.mru')
    if os.path.exists(fn):
        fp = codecs.open(fn, encoding='utf-8')
        a = fp.read().split('\n')
        fp.close()

        mlen = MRU_LEN
        if len(a)>0 and a[0].startswith(MRULENTAG):
            il = int(a[0][len(MRULENTAG):])
            if il > 0:
                mlen = il
            del a[0]
        mrus[n].length = mlen

        for i in a:
            if i and not mrus[n].isin(i):
                mrus[n].add(i)
    else:
        fp = codecs.open(fn, 'w', encoding='utf-8')
        fp.close()
        if not mrus.has_key(n):
            mrus[n] = MRU()
    #print mrus[n]
    return mrus[n]

def in_mru(n, v):
    if not mrus.has_key(n):
        return False
    return mrus[n].isin(v)

def add_mru(n, v):
    if not mrus.has_key(n):
        return
    mrus[n].add(v)

def save_mru(n, newid=None):
    m = mrus[n]
    if newid:
        m.add(newid)
    us = '\n'.join((unicode(i) for i in m.values))

    fn = os.path.join(WDIR, n+'.mru')
    fp = codecs.open(fn, 'w', encoding='utf-8')
    fp.write(MRULENTAG)
    fp.write(unicode(m.length))
    fp.write(u'\n')
    fp.write(us)
    fp.write(u'\n')
    fp.close()

