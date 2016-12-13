import os, os.path, argparse, glob, subprocess

WDIR = os.path.dirname(os.path.realpath(__file__))
ODIR = os.path.join(WDIR, '..', 'out')
ARCDIR = os.path.join(WDIR, '..', 'arc')

def upload_files(dest, dryrun, verbose):
    pargs = ['rsync', '-az' ]
    if dryrun:
        pargs.append('-n')
    if verbose:
        pargs.append('-v')

    files = glob.glob(ODIR+'/*.png')
    if not files:
        print 'Nothing to upload!'
        return
    for fn in files:
        pargs.append(fn)

    pargs.append(dest)
    subprocess.call(pargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('remote_path',
            help='Path to upload to')
    parser.add_argument('-n', '--dry-run',
            dest='dryrun',
            action='store_true',
            help='don\'t actually upload or move anything')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='extra debug spam')
    args = parser.parse_args()

    upload_files(args.remote_path, args.dryrun, args.verbose)

    for fn in glob.glob(ODIR+'/*.png'):
        fn = os.path.realpath(fn)
        if args.verbose:
            print 'rm %s'%(fn)
        if not args.dryrun:
            os.remove(fn)

    for fn in glob.glob(ODIR+'/*.svg'):
        fn = os.path.realpath(fn)
        bn = os.path.basename(fn)
        nfn = os.path.join(ARCDIR, bn)
        if args.verbose:
            print 'mv %s %s'%(fn, nfn)
        if not args.dryrun:
            os.rename(fn, nfn)

