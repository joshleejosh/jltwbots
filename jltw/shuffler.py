# A very silly way to persist shuffled datasets, in order to maintain
# distribution across runs of a program.

import os.path, json, random, codecs, io

class Shuffler:
    CHROFFSET = ord('A')

    def __init__(self):
        self.filename = ''
        self.state = {}

    def load(self, fn):
        self.filename = fn
        if os.path.exists(self.filename):
            fp = io.open(self.filename, encoding='utf-8')
            try:
                self.state = json.load(fp)
            except Exception as e:
                print e
                pass
            fp.close()

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
            #print 'reload %s'%k
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

if __name__ == '__main__':
    import tempfile
    tfd, tfn = tempfile.mkstemp()
    try:
        s = load(tfn)
        assert(len(s.state) == 0)
        a = range(300)

        # first choice fills up state, shuffles, and pops a value
        print s.choice(u'a', a)
        smerge = s.state['a']

        # check persistence
        s.save()
        with open(tfn) as fp:
            print fp.read()

        # Make sure state was persisted and reloaded correctly
        t = load(tfn)
        tmerge = t.state['a']
        assert(smerge == tmerge)

        # exhaust the shuffler.
        b = []
        for i in xrange(299):
            v = t.choice('a', a)
            assert(v not in b)
            b.append(v)
        assert(len(t.state['a']) == 0)
        bmerge = u''.join((unichr(i+ord('A')) for i in b))
        assert(tmerge == bmerge)
        # saved file should contain an empty value for the 'a' key
        t.save()
        with open(tfn) as fp:
            ts = fp.read()
            assert(ts == u'{\n "a": ""\n}')
    finally:
        os.remove(tfn)

