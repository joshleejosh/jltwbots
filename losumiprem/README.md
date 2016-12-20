# LOSUM IPREM - generate rhymes for "Lorem ipsum dolor sit amet."
... or for any phrase you like.

This is not a standalone twitterbot – the dictionary searches are more expensive than they're worth, particularly on static data. This module outputs sentences which can be dumped into a file; jltw.postit can handle posting to twitter.

Requires NLTK with the `cmudict`, `wordnet`, and `names` corpora.

Run `python losumiprem -h` for command line arguments.

Run `python losumiprem/rhymer.py` to rhyme things other than "lorem ipsum."

The general method for rhyming a word:

* Look up the pronunciation of the word in cmudict.
  * If the word doesn't exist, try to find similar words and return those as alternates.
  * You can also specify pronunciations instead of words as arguments to skip this process.
* For each proununciation of the word, find rhymes.
  * Proper rhymes are words with the same number of phonemes as the input word, where the last N phonemes are the same (including stresses);
  * Slant rhymes are words where the phoneme sequence is similar to the input word.
* Filter the result set:
    * Exclude obscure/garbage/blacklist words.
    * Try to guess whether a word is a name and capitalize it.

