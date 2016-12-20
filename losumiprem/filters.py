import os.path
from itertools import chain
import nltk
from nltk.corpus import cmudict, wordnet, names

CWD = os.path.realpath(os.path.dirname(__file__))
nltk.data.path.insert(0, os.path.join(CWD, '..', 'botenv', 'nltk_data'))
CMUD = cmudict.dict()

def in_wordnet(w):
    return len(wordnet.synsets(w)) > 0

# We believe a word is a proper noun iff most uses of the word begin with a
# capital letter.
def is_wordnet_proper(n):
    lemmas = list(chain.from_iterable(syn.lemma_names() for syn in wordnet.synsets(n)))
    proper = filter(lambda i: i[0].isupper(), lemmas)
    return len(proper) > len(lemmas)/2

def in_names(w):
    w = w.title()
    return w in names.words('male.txt') or w in names.words('female.txt')

BLACKLIST = []
with open(os.path.join(CWD, '..', 'secrethist', 'blacklist')) as fp:
    BLACKLIST = [line.strip() for line in fp.readlines()]

def blacklist(p):
    return p.upper() in BLACKLIST

GRAYLIST = []
with open(os.path.join(CWD, 'graylist')) as fp:
    GRAYLIST = [line.strip() for line in fp.readlines() if line[0] != '#']

def graylist(p):
    return p.upper() in GRAYLIST

