# A very silly way to serialize shuffled datasets, in order to maintain
# distribution across runs of a program.

# TODO: this is only using single chrs from 'A' up to represent options, so it
# will crap out on arrays of more than 61 items (give or take).

import os.path, json, random, re

class Shuffler:
    CHROFFSET = 'A'

    def __init__(self):
        self.filename = ''
        self.state = {}

    def load(self, fn):
        self.filename = fn
        if os.path.exists(self.filename):
            fp = open(self.filename)
            self.state = json.load(fp)
            fp.close()

    def save(self, fn=None):
        if fn:
            self.filename = fn
        if not self.filename:
            return
        s = json.dumps(self.state, indent=1)
        fp = open(self.filename, 'w')
        fp.write(s)
        fp.close()

    def choice(self, k, a):
        # load or reload this key into state
        if self.state.has_key(k) and self.state[k]:
            pass
        else:
            #print 'reload %s'%k
            sa = []
            for i in xrange(len(a)):
                sa.append(chr(ord(self.CHROFFSET) + i))
            random.shuffle(sa)
            self.state[k] = ''.join(sa)

        # pick off the first element from this key's shuffled array
        c = ''
        if self.state.has_key(k) and self.state[k]:
            c = self.state[k][0]
            self.state[k] = self.state[k][1:]

        # translate the letter into an array index, then to a value
        rv = ''
        if c:
            i = ord(c) - ord(self.CHROFFSET)
            if i < len(a):
                rv = a[i]
            else:
                #print 'fail: not enough elements for %d in %s (%d: [%s])'%(i, k, len(a), a)
                rv = random.choice(a)
        else:
            #print 'fail, shrug'
            rv = random.choice(a)
        return rv


def load(fn):
    rv = Shuffler()
    rv.load(fn)
    return rv

