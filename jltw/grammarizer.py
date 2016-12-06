# encoding: utf-8
"""
GRAMMARIZER – Why isn't this just Tracery?

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

If the '*fix' key is present and is a list of keys, and those keys are lists,
the lists will be picked from and fixed to a single value BEFORE the grammar is
run. This results in values that are randomized between runs but consistent
within a run.

If the '*include' key is present and is a list of filenames, those files will
be loaded and added to the grammar. Values in the primary file take precedence
over those in included files.

"""

import random, re, copy

KEY_ROOT = "*"
KEY_INCLUDE = "*include"
KEY_FIXEDVAL = "*fix"
RE_TOKEN = re.compile(r'{([^}]*)}')
RE_AAN = re.compile(r'{aan}', re.I)

class Grammarizer(object):

    def __init__(self, g, s):
        if not g:
            g = {u'*':u''}
        self.set_grammar(g)
        self.shuffler = s
        self.doAAnReplacement = True

    def set_grammar(self, g):
        self.grammar = g
        # make sure all keys in the grammar are lowercase.
        for k,v in self.grammar.iteritems():
            del self.grammar[k]
            self.grammar[k.lower()] = v

        if self.grammar.has_key(KEY_INCLUDE):
            d = {}
            includes = self.grammar[KEY_INCLUDE]
            del self.grammar[KEY_INCLUDE]
            if isinstance(includes, basestring):
                includes = (includes,)
            for ifn in includes:
                fp = codecs.open(ifn, encoding='utf-8')
                j = json.load(fp)
                fp.close()
                d.update(j)
            # make sure the grammar is the last set to be applied: if there are
            # conflicts, we want the master file to overwrite included files.
            d.update(self.grammar)
            self.grammar = d

        self.originalGrammar = copy.deepcopy(self.grammar)

    def generate(self):
        # reset
        self.grammar = copy.deepcopy(self.originalGrammar)

        # handle pre-substituted values
        if self.grammar.has_key(KEY_FIXEDVAL):
            fixes = self.grammar[KEY_FIXEDVAL]
            if isinstance(fixes, basestring):
                fixes = (fixes,)
            for k in fixes:
                k = k.lower()
                if self.grammar.has_key(k):
                    a = self.grammar[k]
                    if hasattr(a, '__iter__'):
                        self.grammar[k] = self.replace_tokens(k, a)

        rv = self.replace_tokens(KEY_ROOT, self.grammar[KEY_ROOT])
        if self.doAAnReplacement:
            rv = self.replace_aan(rv)
        return rv

    def replace_tokens(self, key, ins):
        if isinstance(ins, basestring):
            for match in reversed(list(RE_TOKEN.finditer(ins))):
                mkey = match.group(1).strip()

                repl = ''
                if self.doAAnReplacement and mkey.lower() == 'aan':
                    repl = '{%s}'%mkey
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
        '*fix': [ 'sUbJeCt', 'VERB' ],
        '*': '{Aan} {subject} {verb} {aan} {ADJECTIVE} {OBject}{punctuation} That {subject} sure {verb} it!',
        'SUBJECT': ['mouse', 'cat', 'dog', 'elephant', 'iguana'],
        'verb': ['ate', 'chased', 'hugged', 'played with'],
        'Adjective': ['', '', 'effin\'', 'freakin\''],
        'ObJeCt': ['👻' , 'FOAM BALL', 'ostrich egg', 'wooden stick', 'oak leaf', '«speeding ambulance»', 'radio telescope'],
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

