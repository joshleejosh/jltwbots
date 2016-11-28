import os.path, codecs
from collections import defaultdict

MRU_LEN = 48
WDIR = os.path.dirname(os.path.realpath(__file__))
mrus = defaultdict(list)

def load_mru(n):
    fn = os.path.join(WDIR, n)
    if os.path.exists(fn):
        fp = codecs.open(fn, encoding='utf-8')
        a = fp.read().split('\n')
        fp.close()
        for i in a:
            if i not in mrus[n]:
                mrus[n].append(i)
    else:
        fp = codecs.open(fn, 'w', encoding='utf-8')
        fp.close()
        if not mrus.has_key(n):
            mrus[n] = []
    return mrus[n]

def save_mru(n, newid):
    if not mrus.has_key(n):
        return
    if newid in mrus[n]:
        return
    if len(mrus[n]) > MRU_LEN:
        del mrus[n][0]
    mrus[n].append(newid)
    us = '\n'.join((unicode(i) for i in mrus[n]))
    fn = os.path.join(WDIR, n)
    fp = codecs.open(fn, 'w', encoding='utf-8')
    fp.write(us)
    fp.close()

