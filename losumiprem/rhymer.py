# encoding: utf-8
import argparse, sys, re
from collections import defaultdict
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

# Count syllables by counting the number of stress indicators in the pronunciation.
def num_syllables(p):
    return len([
            i[-1]
            for i in p
            if i[-1].isdigit()
            ])

# In Arpabet, stresses are marked: 0=no stress, 1=primary stress, 2=secondary
# stress. This makes sorting annoying.
STRESS_RANK = (0, 2, 1)

# in Arpabet, the stress levels aren't always consistent (ex RUMOUR/TUMOR), and
# stresses are repeated (ex RAFAELA/RUBELLA), so we need to look for the last
# instance of the highest stress value.
def _last_max_stress(p):
    maxi = maxv = 0
    for i in xrange(1, len(p)):
        q = p[-i]
        if q[-1].isdigit():
            v = STRESS_RANK[int(q[-1])]
            if v > maxv:
                maxv = v
                maxi = len(p)-i
    return maxi, maxv

def _split_stress(p):
    if p[-1].isdigit():
        return p[:-1], int(p[-1])
    else:
        return p, 0

# A perfect rhyme is one where the words match from the stressed vowel onwards.
# In Arpabet, stress markers are on the vowels, so we just need to find the
# stress point and match forward from there.
def perfect_rhyme(p, q, syllableTolerance=1):
    if abs(num_syllables(p) - num_syllables(q)) > syllableTolerance:
        return False
    pi, pr = _last_max_stress(p)
    qi, qr = _last_max_stress(q)
    #print p, pr, pi, p[pi:], q, qr, qi, q[qi:]

    if len(p)-pi != len(q)-qi:
        return False

    # the sound just *before* the stress point must differ
    if pi > 0 and qi > 0:
        px, _ = _split_stress(p[pi-1])
        qx, _ = _split_stress(q[qi-1])
        if px == qx:
            return False

    # scan forward from the stress point, stripping out stress markers
    while pi < len(p) and qi < len(q):
        px, pv = _split_stress(p[pi])
        qx, qv = _split_stress(q[qi])
        # we care that a phone is stressed, but not *how* stresed.
        if pv > 0:
            pv = 1
        if qv > 0:
            qv = 1
        if px != qx or pv != qv:
            return False
        pi += 1
        qi += 1
    return True

# just look for decent ending matches
def slant_rhyme(p, q, syllableTolerance=1, matchLength=2):
    if abs(num_syllables(p) - num_syllables(q)) > syllableTolerance:
        return False
    score = 0
    for i in xrange(1, min(len(p), len(q))):
        ps, _ = _split_stress(p[-i])
        ts, _ = _split_stress(q[-i])
        if ps != ts:
            break
        score += 1
    return score >= matchLength

def check_rhyme(p, q):
    if perfect_rhyme(p, q):
        return True
    if slant_rhyme(p, q):
        return True
    #score = levenshtein(p, q)
    #if (0 < score <= similiarityThreshold):
    #    return True
    return False

# ######################################################## #

# Do s contain t or vice versa?
def overlap(s, t):
    s = s.lower()
    t = t.lower()
    if len(s) >= len(t):
        if s.find(t) != -1:
            return True
    if len(t) >= len(s):
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
    if iword in CMUD.iterkeys():
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
    if word in CMUD.iterkeys():
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

def filter_output_word(w):
    return (in_wordnet(w) or in_names(w)) \
            and not blacklist(w) \
            and not graylist(w)

# Find words that rhyme (more or less) with the given word.
# The word may be just a word, or it may be a preformatted Arpabet pronunciation.
# see https://en.wikipedia.org/wiki/Arpabet
def find_rhymes(iword, ffilter=filter_output_word, isarpabetized=False):
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
            similiarityThreshold = min(3, len(pronunciation)/2)
            candidates = []
            for i,w in enumerate(CMUD.iterkeys()):
                ticker(i)
                if w in candidates or w in rv or overlap(w, word):
                    continue
                for p in CMUD[w]:
                    if check_rhyme(pronunciation, p):
                        candidates.append(w)
                        # even if this word has multiple pronunciations,
                        # there's no need to keep checking them.
                        break
            if not candidates:
                vlog(1, 'no candidates', pronunciation)
                continue
            vlog(2, len(candidates))
            rv.extend(candidates)
    if ffilter:
        lenbefore = len(rv)
        rv = filter(ffilter, rv)
        lenafter = len(rv)
        vlog(2, 'Filter', lenbefore, lenafter)
    vlog(1, len(rv))
    return rv

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word', nargs='+',
            help='words to rhyme')
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

    for word in args.word:
        a = find_rhymes(word, isarpabetized=args.arpabet)
        vlog(1, '%d rhymes for %s'%(len(a), word))
        s = ' '.join(a)
        vlog(-99, s)

