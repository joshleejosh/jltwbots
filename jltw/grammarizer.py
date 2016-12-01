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
            rv = self.replaceAAn(rv)
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

                # if we're replacing with an empty string, make sure we don't have extra spaces.
                if not repl and ins[match.end()].isspace():
                    ins = ins[0:match.start()] + ins[match.end()+1:]
                else:
                    ins = ins[0:match.start()] + repl + ins[match.end():]

            return ins

        elif hasattr(ins, '__iter__'):
            v = None
            if self.shuffler:
                v = self.shuffler.choice(key.lower(), ins)
            else:
                v = random.choice(ins)
            return self.replace_tokens(key, v.lower())

        else:
            return ins

    def replaceAAn(self, s):
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
        firstLetter = 0
        for i in xrange(len(tgt)):
            if tgt[i].isalpha() or tgt[i].isdigit():
                firstLetter = i
                break
        if src.isupper():
            rv = tgt.upper()
        elif src[0:2].isupper():
            rv = tgt.title()
        elif src[0].isupper():
            rv = tgt[0:firstLetter] + tgt[firstLetter].upper() + tgt[firstLetter+1:]
        return rv

if __name__ == '__main__':
    grammar = {
            '*': '{Aan} {subject} {verb} {aan} {ADJECTIVE} {OBject}{punctuation}',
            'SUBJECT': ['mouse', 'cat', 'dog', 'elephant', 'iguana'],
            'verb': ['ate', 'chased', 'hugged', 'played with'],
            'Adjective': ['', 'amazing', 'freakin\''],
            'ObJeCt': ['👻' , 'foam ball', 'ostrich egg', 'wooden stick', 'oak leaf', '«speeding ambulance»', 'radio telescope'],
            'punctuation': ['!', '?', '.', '.'],
    }
    gizer = Grammarizer(grammar, None)
    for i in xrange(10):
        print gizer.generate()

