# encoding: utf-8
import os, os.path, argparse, glob, unicodedata, codecs, hashlib, subprocess, tempfile
import jltw.mru
import uniquery, fontquery
from util import *

VERBOSITY = 0
WDIR = os.path.dirname(os.path.realpath(__file__))
DDIR = os.path.join(WDIR, '..', 'out')
MRU_FN = os.path.join(WDIR, '..', 'chars.mru')
TEMPLATE_FN = os.path.join(WDIR, 'svgtemplate.xml')
FONT_DIR = os.path.join(WDIR, '..', 'Noto-unhinted')


def vlog(*args):
    if VERBOSITY > 0:
        print ' '.join((unicode(i) for i in args))

def scrub_output():
    for fn in glob.glob(DDIR+'/[0-9A-F][0-9A-F][0-9A-F][0-9A-F]_*.svg'):
        os.remove(fn)
    for fn in glob.glob(DDIR+'/[0-9A-F][0-9A-F][0-9A-F][0-9A-F]_*.png'):
        os.remove(fn)

SVGTEMPLATE = ''
SZIMAGE = 960
SZBSTROKE = 16
def load_template():
    global SVGTEMPLATE
    with codecs.open(TEMPLATE_FN, encoding='utf-8') as fp:
        SVGTEMPLATE = fp.read()
    templateconsts = {
        'SZFULL'      : SZIMAGE,
        'SZHALF'      : SZIMAGE/2,
        'SZHALFMINUS' : SZIMAGE/2-SZBSTROKE,
        'SZBSTROKE'   : SZBSTROKE,
        }
    for k,v in templateconsts.iteritems():
        SVGTEMPLATE = SVGTEMPLATE.replace(u'«%s»'%k, unicode(v))

def adjust_color_value(iv, hx, amin, amax):
    hv = h2f(hx)
    if hv >= .5:
        hv = morp(hv, 0.5, 1.0, +amin, +amax)
    else:
        hv = morp(hv, 0.0, 0.5, -amax, -amin)
    rv = clamp(iv+hv, 0.0, 1.0)
    vlog(iv, hv, rv)
    return rv

def render_svg(u, fn, fontfn, hv):
    d = {
        'FFN' : fontfn,
        'CC1' : '#000000',
        'CC2' : '#000000',
        'CB1' : '#ffffff',
        'CB2' : '#ffffff',
        'CBS' : 'none',
        'GBX' : '50%',
        'GBY' : '50%',
        'GBR' : '100%',
        'GCX' : '50%',
        'GCY' : '50%',
        'GCR' : '100%',
        }
    if hv:
        a = [hv[i:i+2] for i in xrange(0, len(hv), 2)]
        vlog(hv, ' '.join(a))

        h, s, v = h2f(a[0]), h2f(a[1]), h2f(a[2])
        d['CC1'] = hsv_to_hex(h, s, v)
        vlog(h, s, v, d['CC1'])
        d['CBS'] = d['CC1']

        # CC2 is currently unused - we don't put gradients on text.
        #h = adjust_color_value(h, a[3], 0.0208, 0.0416)
        #s = adjust_color_value(s, a[4], 0.0416, 0.0833)
        #v = adjust_color_value(v, a[5], 0.0416, 0.0833)
        #d['CC2'] = hsv_to_hex(h, s, v)
        #vlog(h, s, v, d['CC2'])

        h, s, v = h2f(a[6]), h2f(a[7]), h2f(a[8])
        # fudge sat and val so we have some room for fading
        s = morp(s, 0.0, 1.0, 0.0333, 0.9667)
        v = morp(v, 0.0, 1.0, 0.0333, 0.9667)
        d['CB1'] = hsv_to_hex(h, s, v)
        vlog(h, s, v, d['CB1'])

        h = adjust_color_value(h, a[ 9], 0.0167, 0.0333)
        s = adjust_color_value(s, a[10], 0.0667, 0.1333)
        v = adjust_color_value(v, a[11], 0.1333, 0.2000)
        d['CB2'] = hsv_to_hex(h, s, v)
        vlog(h, s, v, d['CB2'])

        d['GBX'] = '%d%%'%int(100 * lerp(h2f(a[12]), 0.2000, 0.8000))
        d['GBY'] = '%d%%'%int(100 * lerp(h2f(a[13]), 0.2000, 0.8000))
        d['GBR'] = '%d%%'%int(100 * lerp(h2f(a[14]), 0.7667, 0.9333))
        #d['GCR'] = '%d%%'%int(100 * lerp(h2f(a[15]), 0.7667, 0.9333))
        vlog(d['GBX'], d['GBY'], d['GBR'], d['GCR'])

    fn = os.path.join(DDIR, '%s.svg'%fn)
    svgdata = SVGTEMPLATE.replace(u'«THECHAR»', u)
    for k,v in d.iteritems():
        svgdata = svgdata.replace(u'«%s»'%k,v)
    with codecs.open(fn, 'w', encoding='utf-8') as fp:
        fp.write(svgdata)

def convert_png(fn):
    # OPTION 1: Use quicklook to render a thumbnail of the SVG.
    # Assumes that Gapplin is installed and that its quicklook plugin is doing
    # the rendering. Run `qlmanage -m|grep -i svg` to check. Don't use the
    # default QL SVG renderer, it's terrible with text and fonts.
    # NB: QL thumbnails will always come out square.
    #args = ('qlmanage', '-t', '-s', str(SZIMAGE), '-o', DDIR, DDIR+'/%s.svg'%fn)

    # OPTION 2: Use an Automator workflow to convert from SVG to PNG.
    # Assumes that Gapplin is installed and uses its Automator task for
    # conversion.
    args = ('automator', '-i', DDIR+'/%s.svg'%fn, WDIR+'/../convertsvg.workflow')

    if VERBOSITY > 1:
        subprocess.call(args)
    else:
        tfd, tfn = tempfile.mkstemp()
        try:
            subprocess.call(args, stdout=tfd, stderr=tfd)
        finally:
            os.remove(tfn)

def render_char(u, ffn):
    if u == unichr(0):
        vlog('no char to render, shrug')
        return

    n = unicodedata.name(u, '')
    o = ord(u)
    scat = uniquery.SUPERCATEGORIES[unicodedata.category(u)[0]]
    if VERBOSITY >= 0:
        print u'\t%s\t%04X\t%2s\t%s'%(u, o, scat, n)

    # hash the name to generate pseudorandom values for colors.
    nhash = hashlib.md5(n).hexdigest()
    fn = '%04X_%s'%(o, n)
    render_svg(u, fn, ffn, nhash)
    convert_png(fn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('codes',
            nargs='*',
            help='codepoints to look up. probably won\'t work without specifying a font')
    parser.add_argument('-n', '--num-chars',
            dest='numchars',
            action='store',
            type=int,
            default=1,
            help='number of chars to generate')
    parser.add_argument('-f', '--font-file',
            dest='fontfile',
            action='store',
            type=str,
            help='font to draw characters from')
    parser.add_argument('-d', '--delete-old',
            dest='delold',
            action='store_true',
            help='delete old output files')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='count',
            default=0,
            help='extra debug spam')
    parser.add_argument('-q', '--quiet',
            dest='quiet',
            action='count',
            default=0,
            help='suppress normal output')
    args = parser.parse_args()

    VERBOSITY = args.verbose - args.quiet
    if args.delold:
        scrub_output()

    load_template()
    mru = jltw.mru.MRU(MRU_FN)
    mru.load()

    ffn = ofn = ''
    a = []
    a.extend(((unichr(int(i,16)),args.fontfile) for i in args.codes))
    i = 0
    while i < args.numchars:
        if args.fontfile:
            ffn = args.fontfile
        else:
            ffn = fontquery.random_font(FONT_DIR)

        if ffn != ofn:
            fdata = fontquery.query_font(ffn)
            points = [c[0] for c in fdata if c[0] > 0x1F and c[0] < 0x10000]
            if VERBOSITY > 2:
                print ffn, fontquery.collate_codepoints(sorted(points))
            elif VERBOSITY > 0:
                print ffn
        ofn = ffn

        u = uniquery.randchoice(points)
        if u == unichr(0):
            vlog(u'Failed to find a useful character in [%s]'%ffn)
        elif hex(ord(u)) in mru:
            vlog(u'Char [%s][%X] is in mru'%(u, ord(u)))
        else:
            a.append((u,ffn))
            i += 1

    for u,ffn in a:
        render_char(u, os.path.realpath(ffn))
        mru.add(hex(ord(u)))

    mru.save()

