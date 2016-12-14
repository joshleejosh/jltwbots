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
replacement will be title cased. When the token is lowercase, the replacement
string will be left alone, whatever its case is.)
(TODO: a way to force lowercase?)

{aan} is a magic token that will be replaced with "A" or "AN", depending on the
next word. This can be disabled by setting the doAAnReplacement property to
False.

If the '*fix' key is present and is a list of keys, and those keys are lists,
the lists will be picked from and fixed to a single value BEFORE the grammar is
run. This results in values that are randomized between runs but consistent
within a run.

If the '*include' key is present and is a list of filenames, those files will
be loaded and added to the grammar. Values in the primary file take precedence
over those in included files.

If a token ends with '?' (e.g., {foo?} instead of {foo}), and the token's value
is a list, a blank will be appended to the list to make the value optional. If
the token ends with '??' (e.g., {foo??}), there will be a 50/50 chance of a
blank (instead of 1/len(list)).

"""

import os, random, re, copy, unicodedata
import jltw

KEY_ROOT = "*"
KEY_INCLUDE = "*include"
KEY_FIXEDVAL = "*fix"
RE_TOKEN = re.compile(r'{([^}]*)}')
RE_AAN = re.compile(r'{aan}', re.I)

class Grammarizer(object):

    def __init__(self, g, s, d=os.getcwd()):
        if not g:
            g = {u'*':u''}
        self.includePath = d
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
                ifn = os.path.join(self.includePath, ifn)
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
                        self.grammar[k] = self._replace_tokens(k, a)

        rv = self._replace_tokens(KEY_ROOT, self.grammar[KEY_ROOT])
        if self.doAAnReplacement:
            rv = self._replace_aan(rv)
        return rv

    def _replace_tokens(self, key, ins):
        if isinstance(ins, basestring):
            for match in reversed(list(RE_TOKEN.finditer(ins))):
                mkey = match.group(1).strip()

                addblank = flipblank = False
                if mkey.endswith('??'):
                    mkey = mkey[:-2]
                    flipblank = True
                elif mkey.endswith('?'):
                    mkey = mkey[:-1]
                    addblank = True

                repl = ''
                if self.doAAnReplacement and mkey.lower() == 'aan':
                    repl = '{%s}'%mkey
                else:
                    a = self.grammar[mkey.lower()]
                    if (flipblank or (addblank and isinstance(a, basestring))) and random.random() < .5:
                        a = ""
                    if addblank and not isinstance(a, basestring):
                        a.append('')
                    repl = self._replace_tokens(mkey, a)
                repl = self._caseify(mkey, repl)

                # if we're replacing with an empty string, make sure we
                # don't leave stray spaces in its wake.
                if not repl:
                    ins = self._squeeze_blank(ins, match.start(), match.end())
                else:
                    ins = ins[0:match.start()] + repl + ins[match.end():]

            return ins

        elif hasattr(ins, '__iter__'):
            v = None
            if self.shuffler:
                v = self.shuffler.choice(key.lower(), ins)
            else:
                v = random.choice(ins)
            return self._replace_tokens(key, v)

        else:
            return ins

    def _squeeze_blank(self, ins, si, ei):
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

    def _replace_aan(self, s):
        # a/an replacement
        for m in reversed(list(RE_AAN.finditer(s))):
            # scan to the next letter.
            c = ''
            for i in xrange(m.end(), len(s)):
                c = s[i]
                if c.isalpha() or c.isdigit():
                    break
            # if it's a latin vowel, replace the token with AN, otherwise A.
            article = 'a'
            if c and c.isalpha():
                c = unicode(c)
                c = unicodedata.normalize('NFD', c)[0] # try to strip accents
                if c.lower() in 'aeiou':
                    article = 'an'
            article = self._caseify(m.group(), article)
            s = s[0:m.start()] + article + s[m.end():]
        return s

    # Based on the capitalization of src, change tgt to match.
    def _caseify(self, src, tgt):
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
        '*': '{Aan} {subject} {verb} {aan} {ADJECTIVE??} {OBject}{punctuation} {Coda?}',
        'SUBJECT': [ 'mouse', 'cat', 'dog', 'elephant', 'iguana' ],
        'verb': [ 'ate', 'chased', 'hugged', 'played with' ],
        'Adjective': [ 'effin\'', 'freakin\'' ],
        'ObJeCt': [ u'👻' , 'FOAM BALL', 'ostrich egg', 'wooden stick', 'oak leaf', u'«speeding ambulance»', 'radio telescope' ],
        'punctuation': [ '!', '?', '.', '.'],
        'coda': 'That {subject} sure {verb} it{punctuation}',
    }
    wdir = os.getcwd()
    if gfn.strip():
        fp = codecs.open(gfn, encoding='utf-8')
        grammar = json.load(fp)
        wdir = os.path.dirname(os.path.realpath(gfn))
        fp.close()
    if sfn.strip():
        sh.load(sfn)

    gizer = Grammarizer(grammar, sh, wdir)
    for i in xrange(n):
        jltw.log(gizer.generate())
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

