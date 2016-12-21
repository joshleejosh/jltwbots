# encoding: utf-8
# Persist shuffled sequences across runs of a program.

import os.path, json, random, codecs
import jltw

class Shuffler:
    def __init__(self):
        self.filename = ''
        self.state = {}

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
                rv = random.choice(a)
        else:
            #jltw.log(u'¯\_(ツ)_/¯')
            rv = random.choice(a)
        return rv

    def _refresh(self, k, a):
        #jltw.log('refresh %s'%k)
        sa = range(len(a))
        random.shuffle(sa)
        self.state[k] = sa

