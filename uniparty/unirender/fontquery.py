import glob, random
from itertools import chain
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

# Get supported code points from a font file.
# http://stackoverflow.com/a/19438403
def query_font(fn):
    ttf = TTFont(fn, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=-1)
    #print ttf['name'].names[1]
    chars = chain.from_iterable([y + (Unicode[y[0]],) for y in x.cmap.items()] for x in ttf["cmap"].tables)
    rv = list(chars)
    ttf.close()
    return rv

def random_font(dir):
    files = glob.glob(dir+'/*.ttf')
    return random.choice(files)

# http://stackoverflow.com/a/3430231
# Assume the list is presorted.
from itertools import count, groupby
def collate_codepoints(a):
    # while values increase monotonically, the lambda value will remain constant, and the groupby will lump them together.
    s = groupby(sorted(a), lambda x,c=count(): next(c)-x)
    # make lists out of the grouped values
    t = (list(x) for _,x in s)
    # If there's only one value in each group, only return it, otherwise return the first and last values, which are joined with a dash.
    u = ('-'.join(map(hex, (i[0],i[-1])[:len(i)])) for i in t)
    v = ','.join(u)
    return v

