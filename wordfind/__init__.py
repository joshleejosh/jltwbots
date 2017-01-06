# encoding: utf-8
import jltw, gridslice

GRID_SIZE = 8
MIN_WORDS = 4
MAX_WORDS = 6
MIN_WORDLEN = 4
MAX_WORDLEN = 7

VERBOSE = 0
def set_verbose(v):
    global VERBOSE
    VERBOSE = v

RNG = None
def set_seed(seed):
    import random
    global RNG
    RNG = random.Random(seed)

# ------------------------------------------------------------------ #

WORDLIST = []
BLACKLIST = []
def load_wordlists(fn, bn):
    global WORDLIST, BLACKLIST
    if fn:
        with open(fn) as fp:
            WORDLIST = [line.strip()
                    for line in fp.readlines()
                    if len(line) >= MIN_WORDLEN+1 and len(line) <= MAX_WORDLEN+1
                    ]
    if bn:
        with open(bn) as fp:
            BLACKLIST = [line.strip() for line in fp.readlines()]

# ------------------------------------------------------------------ #

def _word_fits(word, template):
    offsets = range(0, len(template)-len(word)+1)
    RNG.shuffle(offsets)
    for o in offsets:
        wi = 0
        ti = o
        while wi < len(word) and ti < len(template):
            if template[ti] != ' ' and template[ti] != word[wi]:
                break
            wi += 1
            ti += 1
        if wi >= len(word):
            return o
    return -1

def _find_fitting_word(template):
    tlen = len(template)
    if tlen < MIN_WORDLEN:
        raise ValueError('bad template [%s]'%template)

    wordlen = RNG.randint(min(MIN_WORDLEN, tlen), min(MAX_WORDLEN, len(template)))
    if VERBOSE:
        jltw.log(u'find word of [%d] that fits with [%s]'%(wordlen, template))

    candidates = [(w, _word_fits(w,template)) for w in WORDLIST
            if len(w) == wordlen
            and w not in BLACKLIST
            and _word_fits(w, template) != -1
            ]
    if len(candidates) == 0:
        jltw.log('No candidates that fit [%d][%s]'%(wordlen, template))
        raise IndexError
    if VERBOSE:
        jltw.log('%d candidates'%len(candidates))

    word, fit = RNG.choice(candidates)
    if VERBOSE:
        jltw.log(word, fit)
    return word, fit

# ------------------------------------------------------------------ #

def _place_words(grid, di, si, offset, word):
    x, y, dx, dy = gridslice.slice_params(grid, di, si)
    x += dx * offset
    y += dy * offset
    for c in word:
        grid[y][x] = c
        x += dx
        y += dy

def _newgrid():
    return [[' ' for _ in xrange(GRID_SIZE)] for _ in xrange(GRID_SIZE)]

def _copygrid(grid):
    rv = _newgrid()
    for row in xrange(GRID_SIZE):
        for col in xrange(GRID_SIZE):
            rv[row][col] = grid[row][col]
    return rv

def _fill_junk(grid):
    for row in xrange(GRID_SIZE):
        for col in xrange(GRID_SIZE):
            if grid[row][col] == ' ':
                grid[row][col] = chr(RNG.randint(65,90))

def make_grid():
    words = set()
    grid = _newgrid()

    # only do half the directions; we'll handle mirrors below, but we don't
    # want any collisions while looking for slots.
    sa = []
    for d in xrange(0, 4):
        a, b = 0, GRID_SIZE-1
        if d%2 == 1:
            a, b = MIN_WORDLEN-1, (GRID_SIZE*2)-MIN_WORDLEN-1
        for s in xrange(a, b):
            sa.append((d, s))
    RNG.shuffle(sa)

    for i in range(0,RNG.randint(MIN_WORDS, MAX_WORDS)):
        direction, slicei = sa[i]
        # flip this slice?
        if RNG.random() < .5:
            direction = (direction+4)%8

        sliceword = gridslice.cut_slice(grid, direction, slicei)
        if VERBOSE:
            jltw.log(u'%d/%d:[%s]'%(direction, slicei, sliceword))

        try:
            word,offset = _find_fitting_word(sliceword)
        except IndexError:
            continue

        _place_words(grid, direction, slicei, offset, word)
        words.add(word)

    filled = _copygrid(grid)
    _fill_junk(filled)
    return words, grid, filled

