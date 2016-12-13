# UNIPARTY: A party of Unicode characters

There are three parts to this mess:

## uniparty.unirender – Generate SVGs from Unicode characters

Has many (too many) requirements:

* Python FontTools/TTX library (pip install it).
* A directory full of fonts that render diverse Unicode blocks (e.g., Noto).
* Gapplin for nice SVG rendering and PNG conversion.

Generation works in a few steps:

* Pick a font file, and ask it what characters it knows.
* Pick a character, and make a hash of its Unicode name.
* Use the hash value to pick colors.
* Turn it all into a fancy (not very fancy) SVG.
* Convert the SVG into a PNG.

## uniparty.uploader – Upload PNGs to server


## uniparty.bot – Post PNGs to Twitter

* Pick a PNG out of the directory.
* Post it!
* Delete the PNG.

