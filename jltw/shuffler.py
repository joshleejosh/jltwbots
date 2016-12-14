# encoding: utf-8
# A very silly way to persist shuffled datasets, in order to maintain
# distribution across runs of a program.

import os.path, json, random, codecs
import jltw

class Shuffler:
    CHROFFSET = ord('A')

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
            json.dump(self.state, fp, ensure_ascii=False, indent=1)

    def choice(self, k, a):
        # load or reload this key into state
        if self.state.has_key(k) and self.state[k]:
            pass
        else:
            #jltw.log('reload %s'%k)
            sa = []
            for i in xrange(len(a)):
                sa.append(unichr(self.CHROFFSET + i))
            random.shuffle(sa)
            self.state[k] = ''.join(sa)

        # pick off the first element from this key's shuffled array
        c = u''
        if self.state.has_key(k) and self.state[k]:
            c = self.state[k][0]
            self.state[k] = self.state[k][1:]

        # translate the letter into an array index, then to a value
        rv = u''
        if c:
            i = ord(c) - self.CHROFFSET
            if i < len(a):
                rv = a[i]
            else:
                #jltw.log('fail: not enough elements for %d in %s (%d: [%s])'%(i, k, len(a), a))
                rv = random.choice(a)
        else:
            #jltw.log(u'¯\_(ツ)_/¯')
            rv = random.choice(a)
        return rv

def load(fn):
    rv = Shuffler()
    rv.load(fn)
    return rv

