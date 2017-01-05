from sys import version_info, maxunicode

# Get the Unicode codepoint for a single character and/or fullwidth surrogate
# pair. Works in both python2 and python3 (though it's unneccessary in the
# latter, since ord() does what you want it to).
# http://unicodebook.readthedocs.io/unicode_encodings.html
def wideord(c):
    # If we're in py3, then we can handle whatever
    if version_info >= (3,0):
        return ord(c)

    # Or maybe py2 was compiled with ucs4 support
    if maxunicode == 0x10FFFF:
        return ord(c)

    # if this looks like a surrogate pair, then break it down
    if len(c) == 2 and (0xD800 <= ord(c[0]) <= 0xDBFF) and (0xDC00 <= ord(c[1]) <= 0xDFFF):
        oh = (ord(c[0]) & 0x03FF) << 10
        ol = (ord(c[1]) & 0x03FF)
        return 0x10000 + oh + ol
    else:
        return ord(c)

# Get the Unicode character for a codepoint, including fullwidth values above
# 0xFFFF. Works in both python2 and python3 (though it's unneccessary in the
# latter, since chr() does what you want it to).
# http://unicodebook.readthedocs.io/unicode_encodings.html
def widechr(i):
    # If we're in py3, then chr will work for whatever
    if version_info >= (3,0):
        return chr(i)

    # Maybe we're lucky and py2 was compiled with ucs4 support
    if maxunicode == 0x10FFFF:
        return unichr(i)

    if i < 0x10000:
        return unichr(i)

    # Build a fullwidth character out of a surrogate pair
    i -= 0x10000
    ch = (i >> 10) | 0xD800
    cl = (i & 0x3FF) | 0xDC00
    return unichr(ch) + unichr(cl)

