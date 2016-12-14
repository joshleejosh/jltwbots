import os, os.path, argparse, glob, subprocess
import jltw

WDIR = os.path.dirname(os.path.realpath(__file__))
ODIR = os.path.join(WDIR, '..', 'out')

def upload_files(src, dest, dryrun, verbose):
    pargs = ['rsync', '-az' ]
    if dryrun:
        pargs.append('-n')
    if verbose:
        pargs.append('-v')

    files = glob.glob(src+'/*.png')
    if not files:
        jltw.log('Nothing to upload!')
        return
    for fn in files:
        pargs.append(fn)

    pargs.append(dest)
    subprocess.call(pargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir',
            help='Local path to upload PNGs from')
    parser.add_argument('remote_dest',
            help='Remote path (rsync/ssh) to upload PNGs to')
    parser.add_argument('arc_dir',
            help='Local path to archive SVGs to')
    parser.add_argument('-n', '--dry-run',
            dest='dryrun',
            action='store_true',
            help='don\'t actually upload or move anything')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='extra debug spam')
    args = parser.parse_args()

    upload_files(args.src_dir, args.remote_dest, args.dryrun, args.verbose)

    for fn in glob.glob(args.src_dir+'/*.png'):
        fn = os.path.realpath(fn)
        if args.verbose:
            jltw.log('rm %s'%(fn))
        if not args.dryrun:
            os.remove(fn)

    for fn in glob.glob(args.src_dir+'/*.svg'):
        fn = os.path.realpath(fn)
        bn = os.path.basename(fn)
        nfn = os.path.join(args.arc_dir, bn)
        if args.verbose:
            jltw.log('mv %s %s'%(fn, nfn))
        if not args.dryrun:
            os.rename(fn, nfn)

