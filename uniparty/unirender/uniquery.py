# encoding: utf-8
import collections, random, unicodedata
from util import *
import jltw

#jltw.log(u'💪'.encode('unicode-escape'))

def dump():
    for i in xrange(0, 0x10FFFF):
        c = widechr(i)
        n = unicodedata.name(c, '')
        cat = unicodedata.category(c)
        # control characters aren't printable
        if cat.startswith('C'):
            c = u' '
        # combine with space for printing
        if unicodedata.combining(c) != 0:
            c = u' %s'%c
        if cat in ('Zl', 'Zp', 'Zs', 'Sm'):
            jltw.log('%06x: %s: %s / %s'%(i, c, n, cat))

# These names take up huge chunks of the code space.
STALENAMES = (
        'CJK UNIFIED IDEOGRAPH',
        'CJK COMPATIBILITY IDEOGRAPH',
        'HANGUL SYLLABLE',
        )
def stalename(n):
    for sn in STALENAMES:
        if n.startswith(sn):
            return True
    return False

RETRIES = 20

def isusable(o):
    if o < 0x20:
        return False
    u = widechr(o)
    c = unicodedata.category(u)
    if c[0] in ('C', 'Z'):
        return False
    n = unicodedata.name(u, '')
    # ehhh, let's just not, okay?
    if n.upper().find('SVASTI') != -1:
        return False
    return True

def __pickem(f):
    for i in xrange(RETRIES):
        r = f()
        if isusable(r):
            return widechr(r)
    return widechr(0)

# points is a list of codepoints
def randchoice(points):
    return __pickem(lambda: random.choice(points))

def randrange(umin=0x0020, umax=0x10000):
    return __pickem(lambda: random.randrange(umin, umax))

if __name__ == '__main__':
    dump()

