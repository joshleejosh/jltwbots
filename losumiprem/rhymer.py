# encoding: utf-8
import argparse, sys, os, re, random
from collections import defaultdict
import jltw.mru
from losumiprem.filters import *

VERBOSITY = 1
def set_verbosity(v=0, q=0):
    global VERBOSITY
    VERBOSITY = v - q
def vlog(level, *args):
    if VERBOSITY >= level:
        print(' '.join(str(i) for i in args))

# https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_full_matrix
def levenshtein(s, t):
    if len(s) == 0: return len(t)
    if len(t) == 0: return len(s)
    rows, cols = len(s)+1, len(t)+1
    matrix = [range(cols)]
    for i in xrange(1, rows):
        matrix.append([i,] + [0,] * (cols-1))
    for i in xrange(1, rows):
        for j in xrange(1, cols):
            matrix[i][j] = min(
                    matrix[i-1][j  ] + 1,
                    matrix[i  ][j-1] + 1,
                    matrix[i-1][j-1] + (0 if s[i-1]==t[j-1] else 1)
                    )
    return matrix[-1][-1]

RE_DIGIT_END = re.compile(r'\d$')
RE_DIGIT = re.compile(r'\d+')
def trim_stress(a):
    return [RE_DIGIT.sub('', i) for i in a]

def num_syllables(p):
    rv = 0
    for i in p:
        if RE_DIGIT_END.search(i):
            rv += 1
    return rv

# Two words (as phoneme lists) "truly" rhyme if:
# - They have the same number of syllables
# - They have at least N identical phonemes, counting back from the end of the words.
def true_rhyme(s, t):
    if num_syllables(s) != num_syllables(t):
        return False
    score = 0
    for i in xrange(1, min(len(s), len(t))):
        if s[-i] != t[-i]:
            break
        score += 1
    return score >= 2

# Do these two words overlap?
def overlap(s, t):
    s = s.lower()
    t = t.lower()
    if s == t:
        return True
    if s.find(t) != -1:
        return True
    if t.find(s) != -1:
        return True
    return False

PROGRESS_RATE = 20000
def ticker(i):
    if VERBOSITY >= 1 and i%PROGRESS_RATE == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

# If a word is in the CMU dictionary, return it.
# If not, try to find the most "similar" words and return those.
def find_nearest_dictionary_entries(iword, threshold=99):
    iword = iword.lower()
    if iword in CMUD:
        return (iword, CMUD[iword])
    i = 1
    minscore = min(threshold, len(iword))
    candidates = defaultdict(list)
    for i,word in enumerate(CMUD.iterkeys()):
        ticker(i)
        score = levenshtein(iword, word)
        if score <= minscore:
            candidates[score].append((word, CMUD[word]))
            minscore = score
    if candidates:
        best = min(candidates.keys())
        vlog(2, ' '.join((c[0] for c in candidates[best])))
        return candidates[best]
    vlog(2, '%d x'%threshold)
    return []

# If the word is in the CMU corpus, return it and its pronunciation.
# If not, find similar words and return them instead.
def find_pronunciations(word):
    if word in CMUD:
        return [ (word, CMUD[word]), ]
    for t in xrange(1, min(4,len(word)-1)):
        nearby = find_nearest_dictionary_entries(word, threshold=t)
        if nearby:
            rv = []
            for w in nearby:
                vlog(2, u'Substitute', word, t, w)
                rv.append(w)
            return rv
    vlog(2, 'No substitution found', word, t)
    return []

# Find words that rhyme (more or less) with the given word.
# The word may be just a word, or it may be a preformatted Arpabet pronunciation.
# see https://en.wikipedia.org/wiki/Arpabet
def find_rhymes(iword, ffilter=None, isarpabetized=False):
    iword = iword.lower()
    vlog(1, iword.upper())

    alternates = []
    if isarpabetized:
        alternates = [(iword.lower().replace(' ', ''), [iword.upper().split()])]
        iword = iword.lower().replace(' ', '')
    else:
        alternates = find_pronunciations(iword)
    if not alternates:
        vlog(-1, 'No pronunciation found', iword)
        return

    rv = []
    for word,pronunciations in alternates:
        vlog(1, word, pronunciations, ' '.join('-'.join(p) for p in pronunciations))
        if word != iword:
            rv.append(word)
        for pronunciation in pronunciations:
            i = 1
            threshold = min(3, len(pronunciation)/3)
            candidates = []
            for i,w in enumerate(CMUD.iterkeys()):
                ticker(i)
                if overlap(w, word):
                    continue
                for p in CMUD[w]:
                    # look for strict rhymes
                    tr = true_rhyme(pronunciation, p)
                    # look for slant rhymes by looking at similarity of phonemes
                    score = levenshtein(pronunciation, p)
                    if tr or (0 < score <= threshold):
                        candidates.append((w, p))
            if not candidates:
                vlog(1, 'no candidates', pronunciation)
                continue
            vlog(2, len(candidates))
            vlog(4, '\n'.join('%s\t%s'%(c[0], '-'.join(c[1])) for c in candidates))
            rv.extend((c[0] for c in candidates if c[0] not in rv))
    if ffilter:
        lenbefore = len(rv)
        rv = filter(ffilter, rv)
        lenafter = len(rv)
        vlog(2, 'Filter', lenbefore, lenafter)
    vlog(3, ' '.join(rv))
    vlog(1, '%d rhymes for %s'%(len(rv), iword))
    return rv

def main(words, n, mfn, arpabet):
    mru = jltw.mru.MRU(mfn)
    mru.resize(n)
    mru.load()
    result = []
    for word in words:
        a = find_rhymes(word,
            lambda w: (in_wordnet(w) or in_names(w)) and not blacklist(w) and not graylist(w),
            isarpabetized=arpabet)
        a = [w.title() if in_names(w) or is_wordnet_proper(w) else w for w in a]
        result.append(a)
    rv = []
    for i in xrange(n):
        s = ''
        while not s or s in mru:
            s = ' '.join((random.choice(w) for w in result))
        mru.add(s)
        rv.append(s)
    mru.save()
    return rv

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word', nargs='+',
            help='words to rhyme')
    parser.add_argument('-n', '--num-out',
            dest='numout',
            action='store',
            type=int,
            default=1,
            help='number of rhymes to generate')
    parser.add_argument('-a', '--arpabet',
            dest='arpabet',
            action='store_true',
            help='arguments are in arpabet pronunciation format')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='count',
            default=0,
            help='more debug spam')
    parser.add_argument('-q', '--quiet',
            dest='quiet',
            action='count',
            default=0,
            help='less debug spam')
    args = parser.parse_args()

    set_verbosity(args.verbose, args.quiet)
    for sentence in main(args.word, args.numout, '', args.arpabet):
        vlog(-99, sentence)

