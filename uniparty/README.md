# UNIPARTY: A party of Unicode characters

Render random Unicode characters and post them to Twitter (see <a href="https://twitter.com/UnicodeParade">@UnicodeParade</a>).

There are three parts to this mess:

## uniparty.unirender – Generate SVGs from Unicode characters

Has many (too many) requirements:

* Python FontTools library.
* A directory full of fonts that render diverse Unicode blocks (cf. the Google Noto project).
* Gapplin for non-crappy SVG text rendering and PNG conversion.
* Automator (incl. Gapplin's task) to do PNG conversion.

Generation works in a few steps:

* Pick a font file, and ask it what characters it knows.
* Pick a character, and make a hash of its Unicode name.
* Use the hash value to pick colors.
* Turn it all into a fancy (not very fancy) SVG.
* Convert the SVG into a PNG.

## uniparty.uploader – Upload PNGs to server

* Rsync PNGs up to a server.
* Delete uploaded PNGs.
* Move SVGs to an archive directory.

## imgposter – Post PNGs to Twitter

* Pick a random PNG out of the directory.
* Post it!
* Delete the PNG.

