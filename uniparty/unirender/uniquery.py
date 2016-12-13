# encoding: utf-8
import collections, random, unicodedata

#print u'💪'.encode('unicode-escape')

CATEGORIES = collections.defaultdict(str)
CATEGORIES.update({
    'Cc': 'Other, Control',
    'Cf': 'Other, Format',
    'Cn': 'Other, Not Assigned',
    'Co': 'Other, Private Use',
    'Cs': 'Other, Surrogate',
    'LC': 'Letter, Cased',
    'Ll': 'Letter, Lowercase',
    'Lm': 'Letter, Modifier',
    'Lo': 'Letter, Other',
    'Lt': 'Letter, Titlecase',
    'Lu': 'Letter, Uppercase',
    'Mc': 'Mark, Spacing Combining',
    'Me': 'Mark, Enclosing',
    'Mn': 'Mark, Nonspacing',
    'Nd': 'Number, Decimal Digit',
    'Nl': 'Number, Letter',
    'No': 'Number, Other',
    'Pc': 'Punctuation, Connector',
    'Pd': 'Punctuation, Dash',
    'Pe': 'Punctuation, Close',
    'Pf': 'Punctuation, Final quote',
    'Pi': 'Punctuation, Initial quote',
    'Po': 'Punctuation, Other',
    'Ps': 'Punctuation, Open',
    'Sc': 'Symbol, Currency',
    'Sk': 'Symbol, Modifier',
    'Sm': 'Symbol, Math',
    'So': 'Symbol, Other',
    'Zl': 'Separator, Line',
    'Zp': 'Separator, Paragraph',
    'Zs': 'Separator, Space',
    })

SUPERCATEGORIES = collections.defaultdict(str)
SUPERCATEGORIES.update({
    'C': 'Other',
    'L': 'Letter',
    'M': 'Mark',
    'N': 'Number',
    'P': 'Punctuation',
    'S': 'Symbol',
    'Z': 'Separator',
    })

def dump():
    for i in xrange(0, 0x10000):
        c = unichr(i)
        n = unicodedata.name(c, '')
        cat = unicodedata.category(c)
        catcounts[cat] += 1
        # control characters aren't printable
        if cat.startswith('C'):
            c = u' '
        # combine with space for printing
        if unicodedata.combining(c) != 0:
            c = u' %s'%c
        if cat in ('Zl', 'Zp', 'Zs',):
            print '%06x: %s: %s / %s'%(i, c, n, cat)

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

def __pickem(f):
    rv = unichr(0)
    for i in xrange(RETRIES):
        r = f()
        u = unichr(r)
        c = unicodedata.category(u)
        if c[0] in ('C', 'Z'):
            continue
        n = unicodedata.name(u, '')
        # ehhh, let's just not, okay?
        if n.upper().find('SVASTI') != -1:
            continue
        return u
    return rv

# points is a list of codepoints
def randchoice(points):
    return __pickem(lambda: random.choice(points))

def randrange(umin=0x0020, umax=0x10000):
    return __pickem(lambda: random.randrange(umin, umax))

