# encoding: utf-8
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

# -------------------------------------------------------- #

ARPABET_TO_IPA = {
    #u'AA R' : u'ɑr',  # large (L AA1 R JH); hard (HH AA1 R D)
    u'AA'   : u'ɑ',   # father (F AA1 DH ER), cot (K AA1 T)
    u'AE'   : u'æ',   # at (AE1 T); fast (F AE1 S T)
    u'AH'   : u'ə',   # sofa (S OW1 F AH0), alone (AH0 L OW1 N)
    #u'AH'   : u'ʌ',   # but (B AH1 T), sun (S AH1 N)
    #u'AO R' : u'ɔr',  # more (M AO1 R); bored (B AO1 R D); chord (K AO1 R D)
    u'AO'   : u'ɔ',   # off (AO1 F); fall (F AO1 L); frost (F R AO1 S T)
    #u'AW R' : u'aʊr', # This seems to be a rarely used r-controlled vowel. In some dialects flower (F L AW1 R; in other dialects F L AW1 ER0)
    u'AW'   : u'aʊ',  # how (HH AW1); now (N AW1)
    u'AX'   : u'ə',   # discus (D IH1 S K AX0 S); note distinction from discuss (D IH0 S K AH1 S)
    u'AXR'  : u'ɚ',   # father (F AA1 DH AXR); coward (K AW1 AXR D)
    u'AY'   : u'aɪ',  # my (M AY1); why (W AY1); ride (R AY1 D)
    u'B'    : u'b',   # buy (B AY1)
    u'CH'   : u'tʃ',  # chair (CH EH1 R)
    u'D'    : u'd',   # day (D EY1)
    u'DH'   : u'ð',   # that (DH AE1 T); the (DH AH0); them (DH EH1 M)
    u'DX'   : u'ɾ',   # wetter (W EH1 DX AXR)
    #u'EH R' : u'ɛr',  # air (EH1 R); where (W EH1 R); hair (HH EH1 R)
    u'EH'   : u'ɛ',   # red (R EH1 D); men (M EH1 N)
    u'EL'   : u'ɫ̩',   # bottle (B AO1 DX EL)
    u'EM'   : u'm̩',   # keep 'em (K IY1 P EM)
    u'EN'   : u'n̩',   # button (B AH1 T EN)
    u'ENG'  : u'ŋ̍',   # Washington (W AO1 SH ENG T EN)
    u'ER'   : u'ɝ',   # her (HH ER0); bird (B ER1 D); hurt (HH ER1 T), nurse (N ER1 S)
    u'EY'   : u'eɪ',  # say (S EY1); eight (EY1 T)
    u'F'    : u'f',   # for (F AO1 R)
    u'G'    : u'ɡ',   # go (G OW1)
    u'HH'   : u'h',   # house (HH AW1 S)
    #u'IH R' : u'ɪr',  # ear (IY1 R); near (N IH1 R)
    u'IH'   : u'ɪ',   # big (B IH1 G); win (W IH1 N)
    #u'IY R' : u'ɪr',  # ear (IY1 R); near (N IH1 R)
    u'IY'   : u'i',   # bee (B IY1); she (SH IY1)
    u'JH'   : u'dʒ',  # just (JH AH1 S T); gym (JH IH1 M)
    u'K'    : u'k',   # key (K IY1)
    u'L'    : u'ɫ',   # late (L EY1 T)
    u'M'    : u'm',   # man (M AE1 N)
    u'N'    : u'n',   # no (N OW1)
    u'NG'   : u'ŋ',   # sing (S IH1 NG)
    u'NX'   : u'ɾ̃',   # wintergreen (W IY2 NX AXR G R IY1 N)
    u'OW'   : u'oʊ',  # show (SH OW1); coat (K OW1 T)
    u'OY'   : u'ɔɪ',  # boy (B OY1); toy (T OY1)
    u'P'    : u'p',   # pay (P EY1)
    u'Q'    : u'ʔ',   # (glottal stop) uh-oh (Q AH1 Q OW) (ʔʌʔoʊ)
    u'R'    : u'r',   # run (R AH1 N)
    #u'R'    : u'ɹ',   # run (R AH1 N)
    u'S'    : u's',   # say (S EY1)
    u'SH'   : u'ʃ',   # show (SH OW1)
    u'T'    : u't',   # take (T EY1 K)
    u'TH'   : u'θ',   # thanks (TH AE1 NG K S); Thursday (TH ER1 Z D EY2)
    #u'UH R' : u'ʊr',  # cure (K Y UH1 R); bureau (B Y UH1 R OW0), detour (D IH0 T UH1 R)
    u'UH'   : u'ʊ',   # should (SH UH1 D), could (K UH1 D)
    u'UW'   : u'u',   # you (Y UW1); new (N UW1); food (F UW1 D)
    u'V'    : u'v',   # very (V EH1 R IY0)
    u'W'    : u'w',   # way (W EY1)
    u'Y'    : u'j',   # yes (Y EH1 S)
    u'Z'    : u'z',   # zoo (Z UW1)
    u'ZH'   : u'ʒ',   # measure (M EH1 ZH ER0); pleasure (P L EH1 ZH ER)
}

