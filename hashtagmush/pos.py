# coding=utf-8
import os.path, random, re, codecs
from collections import defaultdict
import nltk

WDIR = os.path.dirname(os.path.realpath(__file__))
nltk.data.path.insert(0, os.path.join(WDIR, '..', 'botenv', 'nltk_data'))

def pos_buckets(sentence):
    rv = defaultdict(list)
    wt = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(wt)
    for pair in tagged:
        rv[pair[1]].append(pair[0])
    return rv

def floop(wordlist):
    posbuckets = defaultdict(list)
    wt = nltk.word_tokenize(' '.join(wordlist))
    tagged = nltk.pos_tag(wt, 'brown')
    for word,pos in tagged:
        if pos == 'VBG':
            posbuckets['VERBING'].append(word)
        elif pos.startswith('J'):
            posbuckets['ADJECTIVE'].append(word)
        elif pos.startswith('NNP'):
            posbuckets['PROPER'].append(word)
        elif pos.startswith('NN'):
            posbuckets['NOUN'].append(word)
        else:
            posbuckets[pos].append(word)

    for pos,words in posbuckets.iteritems():
        print pos, ' '.join(words).encode('utf-8')

    if posbuckets['ADJECTIVE']:
        quality = caseify(random.choice(posbuckets['ADJECTIVE']))

    candidates = []
    if posbuckets['NOUN'] or posbuckets['VERBING']:
        candidates = posbuckets['NOUN'] + posbuckets['VERBING']
    else:
        pass

RE_URL = re.compile(r'http\S*')
def stripurls(sentence):
    return RE_URL.sub('', sentence)

def munge(sentences):
    buckets = defaultdict(list)
    for sentence in sentences:
        sentence = stripurls(sentence)
        wt = nltk.word_tokenize(sentence)
        #tagger = nltk.tag.hmm.HiddenMarkovModelTagger()
        tagged = nltk.pos_tag(wt)
        for word,pos in tagged:
            if word not in buckets[pos]:
                buckets[pos].append(word)
    for pos,words in buckets.iteritems():
        print pos, ' '.join(words).encode('utf-8')



if __name__ == '__main__':
    fp = codecs.open('t', encoding='utf-8')
    sentences = fp.read().split('\n')
    fp.close()
    munge(sentences)
