# encoding: utf-8
import argparse, time, copy
import jltw
from unihelp import widechr
import wordfind

# How many frickin alphabets do we need anyway?
A_VARIANTS = [
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

def squarify(s, v=34):
    rv = u''
    for c in s.upper():
        if 'A' <= c <= 'Z':
            i = ord(c) - A_VARIANTS[0]
            rv += widechr(A_VARIANTS[v] + i)
        elif c == ' ':
            rv += widechr(A_VARIANTS[v]+8)
        else:
            rv += c
    return rv

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('wordlist')
    parser.add_argument('blacklist')
    parser.add_argument('-t', '--tweet',
            dest='tweet',
            action='store',
            type=str,
            default='',
            help='post to twitter, with credentials in given file.')
    parser.add_argument('-s', '--seed',
            dest='seed',
            action='store',
            type=int,
            default=int(time.time()),
            help='seed value for randomizer')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='print debug spam')
    args = parser.parse_args()

    wordfind.set_verbose(args.verbose)
    wordfind.set_seed(args.seed)
    wordfind.load_wordlists(args.wordlist, args.blacklist)

    api = None
    if args.tweet:
        api = jltw.open_twitter(args.tweet)

    words, bare, filled = wordfind.make_grid()
    jltw.log('%s\n\n%s\n\n%s'%(' '.join(list(words)), bare, filled))

    if args.tweet:
        tweet = u'%s\n%s'%(' '.join(list(words)), squarify(filled))
        api.PostUpdate(tweet, verify_status_length=False)

