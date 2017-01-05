# encoding: utf-8
import jltw
from unihelp import widechr

# How many frickin alphabets do we need anyway?
_ALPHABETS = [
        0x41, # LATIN CAPITAL LETTER A – A
        0x61, # LATIN SMALL LETTER A – a
        0x249c, # PARENTHESIZED LATIN SMALL LETTER A – ⒜
        0x24b6, # CIRCLED LATIN CAPITAL LETTER A – Ⓐ
        0x24d0, # CIRCLED LATIN SMALL LETTER A – ⓐ
        0x1d400, # MATHEMATICAL BOLD CAPITAL A – 𝐀
        0x1d41a, # MATHEMATICAL BOLD SMALL A – 𝐚
        0x1d434, # MATHEMATICAL ITALIC CAPITAL A – 𝐴
        0x1d44e, # MATHEMATICAL ITALIC SMALL A – 𝑎
        0x1d468, # MATHEMATICAL BOLD ITALIC CAPITAL A – 𝑨
        0x1d482, # MATHEMATICAL BOLD ITALIC SMALL A – 𝒂
        0x1d468, # MATHEMATICAL BOLD ITALIC CAPITAL A – 𝑨
        0x1d482, # MATHEMATICAL BOLD ITALIC SMALL A – 𝒂
        0x1d49c, # MATHEMATICAL SCRIPT CAPITAL A – 𝒜
        0x1d4b6, # MATHEMATICAL SCRIPT SMALL A – 𝒶
        0x1d4d0, # MATHEMATICAL BOLD SCRIPT CAPITAL A – 𝓐
        0x1d4ea, # MATHEMATICAL BOLD SCRIPT SMALL A – 𝓪
        0x1d504, # MATHEMATICAL FRAKTUR CAPITAL A – 𝔄
        0x1d51e, # MATHEMATICAL FRAKTUR SMALL A – 𝔞
        0x1d538, # MATHEMATICAL DOUBLE-STRUCK CAPITAL A – 𝔸
        0x1d552, # MATHEMATICAL DOUBLE-STRUCK SMALL A – 𝕒
        0x1d56c, # MATHEMATICAL BOLD FRAKTUR CAPITAL A – 𝕬
        0x1d586, # MATHEMATICAL BOLD FRAKTUR SMALL A – 𝖆
        0x1d5a0, # MATHEMATICAL SANS-SERIF CAPITAL A – 𝖠
        0x1d5ba, # MATHEMATICAL SANS-SERIF SMALL A – 𝖺
        0x1d5d4, # MATHEMATICAL SANS-SERIF BOLD CAPITAL A – 𝗔
        0x1d5ee, # MATHEMATICAL SANS-SERIF BOLD SMALL A – 𝗮
        0x1d608, # MATHEMATICAL SANS-SERIF ITALIC CAPITAL A – 𝘈
        0x1d622, # MATHEMATICAL SANS-SERIF ITALIC SMALL A – 𝘢
        0x1d63c, # MATHEMATICAL SANS-SERIF BOLD ITALIC CAPITAL A – 𝘼
        0x1d656, # MATHEMATICAL SANS-SERIF BOLD ITALIC SMALL A – 𝙖
        0x1d670, # MATHEMATICAL MONOSPACE CAPITAL A – 𝙰
        0x1d68a, # MATHEMATICAL MONOSPACE SMALL A – 𝚊
        0x1f110, # PARENTHESIZED LATIN CAPITAL LETTER A – 🄐
        0x1f130, # SQUARED LATIN CAPITAL LETTER A – 🄰
        0x1f150, # NEGATIVE CIRCLED LATIN CAPITAL LETTER A – 🅐
        0x1f170, # NEGATIVE SQUARED LATIN CAPITAL LETTER A – 🅰
        0x1f1e6, # REGIONAL INDICATOR SYMBOL LETTER A – 🇦
        ]

def _fmt_chr(c, v=34):
    if 'A' <= c <= 'Z':
        i = ord(c) - _ALPHABETS[0]
        return widechr(_ALPHABETS[v] + i)
    elif c == ' ':
        return widechr(_ALPHABETS[v]+8) # shrug
    return c

def _fmt_str(s, v=34):
    rv = u''
    for c in s.upper():
        rv += _fmt_chr(c, v)
    return rv

def _join_grid(grid):
    return u'\n'.join(
            u''.join(c for c in row)
            for row in grid
            )

# format a puzzle with a list of words and one or more grids.
# If 'replace' is true, replace letters in the grids with fancy unicode.
def format_text(words, *grids, **kwargs):
    rv = u' '.join(list(words))
    for g in grids:
        rv += u'\n'
        gs = _join_grid(g)
        if 'replace' in kwargs and kwargs['replace']:
            gs = _fmt_str(gs)
        rv += gs
        rv += u'\n'
    return rv

# return a formatted grid with solution letters marked.
# Unicode replacement is always enabled for this function (since we need it to mark letters)
def format_solution(words, solution, grid):
    rv = u' '.join(list(words))
    rv += '\n'
    for row in xrange(len(grid)):
        for col in xrange(len(grid)):
            gc = grid[row][col]
            sc = solution[row][col]
            if 'A' <= sc <= 'Z':
                rv += _fmt_chr(gc, 36)
            else:
                rv += _fmt_chr(gc, 34)
        rv += '\n'
    return rv

