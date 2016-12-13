# encoding: utf-8
import os.path, argparse, glob, random
import jltw, jltw.mru

DRYRUN = False
VERBOSE = False
RETRIES = 20
WDIR = os.path.dirname(os.path.realpath(__file__))
MRU_FN = os.path.join(WDIR, '..', 'bot.mru')

mru = None

def vlog(*args):
    if VERBOSE:
        print ' '.join((unicode(i).encode('utf-8') for i in args))

def pick_file(dir):
    files = glob.glob(dir+'/*.png')
    if not files:
        return ''
    return random.choice(files)

# The filename has everything we need to make the text for our tweet.
def make_text(fn):
    fn = os.path.splitext(os.path.basename(os.path.realpath(fn)))[0]
    a = fn.split('_')
    i = int(a[0], 16)
    u = unichr(i)
    #rv = u'0x%04X – %s – %s'%(i, ' '.join(a[1:]), u)
    rv = u'%s – %s'%(u, ' '.join(a[1:]))
    return rv

def del_file(fn):
    if not DRYRUN:
        if VERBOSE:
            print 'rm %s'%fn
        os.remove(fn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('srcdir',
            help='dir with files to choose from')
    parser.add_argument('authfile',
            help='file containing twitter credentials')
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

    mru = jltw.mru.MRU(MRU_FN)
    mru.load()

    fn = args.forcefile
    if not fn:
        fn = pick_file(args.srcdir)
        if not fn:
            print 'FAILURE: No images to upload!'
            exit(0)
        for retryi in xrange(RETRIES):
            fn = os.path.realpath(fn)
            bn = os.path.splitext(os.path.basename(fn))[0]
            if bn in mru:
                vlog('MRU hit [%s]'%bn)
                del_file(fn)
                fn = pick_file(args.srcdir)
            else:
                break

    text = make_text(fn)
    print text.encode('utf-8')

    if not DRYRUN:
        if args.tweet:
            with open(fn, 'rb') as fp:
                api = jltw.open_twitter(args.authfile)
                api.PostUpdate(text, media=fp)
        mru.add(os.path.splitext(os.path.basename(fn))[0])

    del_file(fn)
    if not DRYRUN:
        mru.save()

