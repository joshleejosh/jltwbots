# encoding: utf-8
import sys, os
from collections import defaultdict
import nltk
from nltk.corpus import cmudict, wordnet, names

CWD = os.path.realpath(os.path.dirname(__file__))
nltk.data.path.insert(0, os.path.join(CWD, '..', 'botenv', 'nltk_data'))
CMUD = cmudict.dict()

if __name__ == '__main__':
    w = 'molar'
    if len(sys.argv) > 1:
        w = sys.argv[1]

    print '--- CMUDICT --------------------------'
    if w.lower() not in CMUD:
        print '[%s] is not in cmudict'%w
    else:
        print w.lower(), CMUD[w.lower()]

    print '--- WORDNET --------------------------'
    sa = wordnet.synsets(w)
    if not sa:
        print '[%s] is not in wordnet'%w
    else:
        for syn in sa:
            print syn.name(), syn.lexname()
            print '    ' + '; '.join(syn.lemma_names())
            print '    ' + syn.definition()[0:40] + ('...' if len(syn.definition())>40 else '')
            for ex in syn.examples():
                print '        ' + ex

    print '--- NAMES ----------------------------'
    y = False
    for fn in ('male', 'female'):
        if w.title() in names.words('%s.txt'%fn):
            y = True
            print '[%s] is a %s name'%(w.title(), fn)
    if not y:
        print '[%s] is not a name'%w.title()

