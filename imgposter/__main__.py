# encoding: utf-8
"""
IMGPOSTER: Post a random image from a directory to Twitter.
The filename (minus path and extension) is the text of the tweet.
"""

import os.path, argparse, glob, random
import jltw, jltw.mru

DRYRUN = False
VERBOSE = False
RETRIES = 20
WDIR = os.path.dirname(os.path.realpath(__file__))

def vlog(*args):
    if VERBOSE:
        jltw.log(u' '.join((unicode(i) for i in args)))

def pick_file(dir):
    files = glob.glob(dir+'/*.png')
    if not files:
        return ''
    return random.choice(files)

def del_file(fn):
    vlog(u'rm %s'%fn.decode('utf-8'))
    if not DRYRUN:
        os.remove(fn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('srcdir',
            help='dir with files to choose from')
    parser.add_argument('authfile',
            help='file containing twitter credentials')
    parser.add_argument('-m', '--mru',
            dest='mrufile',
            action='store',
            type=str,
            help='mru list to check/maintain')
    parser.add_argument('-f', '--file',
            dest='forcefile',
            action='store',
            type=str,
            help='specify a file to process (ignore srcdir) (file will be scrubbed after upload!)')
    parser.add_argument('-t', '--tweet',
            action='store_true',
            dest='tweet',
            help='post the result to twitter')
    parser.add_argument('-n', '--dry-run',
            dest='dryrun',
            action='store_true',
            help='don\'t actually do anything')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='extra debug spam')
    args = parser.parse_args()

    DRYRUN = args.dryrun
    VERBOSE = args.verbose

    mru = jltw.mru.MRU()
    if args.mrufile:
        mru = jltw.mru.MRU(os.path.realpath(args.mrufile))
        mru.load()

    fn = args.forcefile
    if not fn:
        fn = pick_file(args.srcdir)
        if not fn:
            jltw.log('FAILURE: No images to upload!')
            exit(0)
        for retryi in xrange(RETRIES):
            fn = os.path.realpath(fn)
            bn = os.path.splitext(os.path.basename(fn))[0].decode('utf-8')
            if bn in mru:
                vlog('MRU conflict [%s]'%bn)
                del_file(fn)
                fn = pick_file(args.srcdir)
            else:
                break

    text = os.path.splitext(os.path.basename(fn))[0].decode('utf-8')
    jltw.log(text)

    if not DRYRUN:
        if args.tweet:
            with open(fn, 'rb') as fp:
                api = jltw.open_twitter(args.authfile)
                api.PostUpdate(text, media=fp)
        mru.add(os.path.splitext(os.path.basename(fn))[0].decode('utf-8'))

    del_file(fn)
    if not DRYRUN:
        mru.save()

