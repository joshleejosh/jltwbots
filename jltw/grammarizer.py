# encoding: utf-8
"""
Begin with the "*" key, and replace any {whatever} tokens you run into with the
appropriate value, recursing where appropriate.

If you encounter an array, choose randomly from its elements.

All keys are case insensitive, and are transformed to lowercase when the
grammar is initialized.

When a token is all-caps or begins with an uppercase letter, the replacement
will be similarly capitalized. When the first TWO letters are uppercase, the
replacement will be title cased. When the key is lowercase, the replacement
string will be left alone, whatever its case is.)

{aan} is a magic key that will be replaced with "A" or "AN", depending on the
next word. This can be disabled by setting the doAAnReplacement property to
False.
"""

import random, re

RE_TOKEN = re.compile(r'{([^}]*)}')
RE_AAN = re.compile(r'{aan}', re.I)

class Grammarizer(object):

    def __init__(self, g, s):
        if not g:
            g = {'*':''}
        self.grammar = g
        self.shuffler = s
        self.doAAnReplacement = True

        # make sure all keys in the grammar are lowercase.
        for k,v in self.grammar.iteritems():
            del self.grammar[k]
            self.grammar[k.lower()] = v

    def generate(self):
        rv = self.replace_tokens('*', self.grammar['*'])
        if self.doAAnReplacement:
            rv = self.replace_aan(rv)
        return rv

    def replace_tokens(self, key, ins):
        if isinstance(ins, basestring):
            for match in reversed(list(RE_TOKEN.finditer(ins))):
                mkey = match.group(1).strip()

                repl = ''
                if self.doAAnReplacement and mkey.lower() == 'aan':
                    repl = '{%s}'%(self.caseify(mkey, 'aan'))
                else:
                    repl = self.replace_tokens(mkey, self.grammar[mkey.lower()])
                repl = self.caseify(mkey, repl)

                # if we're replacing with an empty string, make sure we
                # don't leave stray spaces in its wake.
                if not repl:
                    ins = self.squeeze_blank(ins, match.start(), match.end())
                else:
                    ins = ins[0:match.start()] + repl + ins[match.end():]

            return ins

        elif hasattr(ins, '__iter__'):
            v = None
            if self.shuffler:
                v = self.shuffler.choice(key.lower(), ins)
            else:
                v = random.choice(ins)
            return self.replace_tokens(key, v)

        else:
            return ins

    def squeeze_blank(self, ins, si, ei):
        repl = ''
        if si == 0:
            while ei<len(ins) and ins[ei].isspace():
                ei += 1
        elif ei == len(ins):
            while ins[si-1].isspace():
                si -= 1
        else:
            if ins[si-1].isspace() or (ei<len(ins) and ins[ei].isspace()):
                repl = ' '
            while ins[si-1].isspace():
                si -= 1
            while ei<len(ins) and ins[ei].isspace():
                ei += 1
        ins = ins[0:si] + repl + ins[ei:]
        return ins

    def replace_aan(self, s):
        # a/an replacement
        for m in reversed(list(RE_AAN.finditer(s))):
            # scan to the next letter.
            c = ''
            for i in xrange(m.end(), len(s)):
                c = s[i]
                if c.isalpha() or c.isdigit():
                    break
            # if it's a vowel, replace the token with AN, otherwise A.
            article = 'a'
            if c and c.lower() in 'aeiou':
                article = 'an'
            article = self.caseify(m.group(), article)
            s = s[0:m.start()] + article + s[m.end():]
        return s

    # Based on the capitalization of src, change tgt to match.
    def caseify(self, src, tgt):
        src = src.strip().strip('{}')
        rv = tgt
        firstLetter = -1
        for i in xrange(len(tgt)):
            if tgt[i].isalpha() or tgt[i].isdigit():
                firstLetter = i
                break
        if src.isupper():
            rv = tgt.upper()
        elif src[0:2].isupper():
            rv = tgt.title()
        elif src[0].isupper() and firstLetter > -1:
            rv = tgt[0:firstLetter] + tgt[firstLetter].upper() + tgt[firstLetter+1:]
        return rv

def main(gfn, sfn, n):
    sh = shuffler.Shuffler()
    grammar = {
        '*': '{Aan} {subject} {verb} {aan} {ADJECTIVE} {OBject}{punctuation}',
        'SUBJECT': ['mouse', 'cat', 'dog', 'elephant', 'iguana'],
        'verb': ['ate', 'chased', 'hugged', 'played with'],
        'Adjective': ['', 'effin\'', 'freakin\''],
        'ObJeCt': ['👻' , 'foam ball', 'ostrich egg', 'wooden stick', 'oak leaf', '«speeding ambulance»', 'radio telescope'],
        'punctuation': ['!', '?', '.', '.'],
    }
    if gfn:
        fp = codecs.open(gfn, encoding='utf-8')
        grammar = json.load(fp)
        fp.close()
    if sfn:
        sh.load(sfn)

    gizer = Grammarizer(grammar, sh)
    for i in xrange(n):
        print gizer.generate()
    if sfn:
        sh.save()

if __name__ == '__main__':
    import argparse, codecs, json, shuffler
    parser = argparse.ArgumentParser()
    parser.add_argument('grammarfile', type=str, nargs='?')
    parser.add_argument('shufflefile', type=str, nargs='?')
    parser.add_argument('num', type=int, nargs='?', default=1)
    args = parser.parse_args()
    main(args.grammarfile, args.shufflefile, args.num)

