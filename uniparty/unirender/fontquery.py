import glob
from itertools import chain
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
import jltw.shuffler
import uniquery
from util import *

_shuf_fn = ''
_shuf = None

# Lots of fonts contain ASCII chars for compatibility, but we only want them
# from the fonts that we want them from, y'know what I mean?
ASCIIFONTS = ( 'NotoSerif-Regular', 'NotoSans-Regular', 'NotoMono-Regular', )

# Get supported code points out of a font file.
# http://stackoverflow.com/a/19438403
def query_font(fn):
    rv = []
    ttf = TTFont(fn, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=-1)
    try:
        #jltw.log(ttf['name'].names[1])
        chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
        rv = list(chars)
    finally:
        ttf.close()
    return rv

def query_font_prefiltered(fn):
    rv = []
    ttf = TTFont(fn, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=-1)
    try:
        chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
        rv = [c[0] for c in chars if _filter_char(c[0], basebase(fn))]
    finally:
        ttf.close()
    return rv

def _filter_char(o, fn):
    if fn and fn not in ASCIIFONTS and o < 0x80:
        return False
    return uniquery.isusable(o)

def random_font(dir):
    global _shuf
    if not _shuf:
        _shuf = jltw.shuffler.load(_shuf_fn)
    files = sorted(glob.glob(dir+'/*.[to]tf'))
    rv = _shuf.choice('f', files)
    _shuf.save()
    return rv

def set_shuffler(fn):
    global _shuf_fn
    if fn:
        fn = os.path.realpath(fn)
    _shuf_fn = fn

# Turn a big list of values into a more friendly set of ranges.
# http://stackoverflow.com/a/3430231
from itertools import count, groupby
def collate_codepoints(a):
    # filter out dupes and sort
    a = sorted(set(a))
    # while values increase monotonically alongside the counter, the lambda
    # value will remain constant, and the groupby will lump them together.
    s = groupby(a, lambda i,c=count(): next(c)-i)
    # make lists out of the grouped values
    t = (list(i) for _,i in s)
    # If there's only one value in each group, only return it, otherwise return
    # the first and last values, which are joined with a dash.
    # Also convert to hex somewhere along the way.
    u = ((i[0],i[-1])[:len(i)] for i in t)
    v = (map(lambda j: '%x'%j, i) for i in u)
    x = ('-'.join(i) for i in v)
    y = ','.join(x)
    return y


def dump_catalog(dir):
    for fn in sorted(glob.glob(dir+'/*.[to]tf')):
        fn = os.path.realpath(fn)
        a = query_font_prefiltered(fn)
        jltw.log('%s\t%d\t%s'%(basebase(fn), len(a), collate_codepoints(a)))

if __name__ == '__main__':
    import os.path, collections
    dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Noto-unhinted'))
    dump_catalog(dir)

