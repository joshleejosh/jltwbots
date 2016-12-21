import sys, os, glob, random, codecs, argparse, re
import jltw

"""
Pick a note from a database and post it.

The database can either be:
    * A directory full of files, one note per file.
    * A text file with one note per line.

For the directory method, a note file can specify a couple of extra things:
    * An ID for sorting/MRU management
    * A media file to attach to the post.

When a note is chosen and posted, it is removed from the database.

Notes can be posted in order or randomly.

"""

DRYRUN = VERBOSE = RANDOMIZE = False

RE_HEADER = re.compile(r'^(\w+):(.*)$')

def vlog(*args, **kwargs):
    if VERBOSE or ('force' in kwargs and kwargs['force']):
        jltw.log(*args)

class Note(object):
    def __init__(self, i, t, m='', fn=''):
        self.id = i
        self.text = t
        self.media = m
        self.filename = fn

# ######################################################## #

def note_from_file(fn):
    lines = []
    with codecs.open(fn, encoding='utf-8') as fp:
        lines = fp.readlines()

    id = media = ''
    i=0
    while RE_HEADER.match(lines[i]):
        m = RE_HEADER.match(lines[i])
        k = m.group(1)
        v = m.group(2)
        if k.lower() == 'id':
            id = v.strip()
        if k.lower() == 'media':
            media = v.strip()
        i += 1
    text = ''.join(lines[i:])
    return Note(id, text, media, fn)

def pick_from_dir(dir):
    notes = []
    for fn in glob.glob(dir+'/*'):
        fn = os.path.realpath(fn)
        if os.path.isfile(fn):
            notes.append(note_from_file(fn))
    notes.sort(key=lambda i: i.id)

    i = 0
    if RANDOMIZE:
        i = random.randint(0, len(notes))
    note = notes[i]

    vlog('rm %s'%note.filename)
    if not DRYRUN:
        os.remove(note.filename)

    return note

def pick_from_file(fn):
    lines = []
    with codecs.open(fn, encoding='utf-8') as fp:
        lines = fp.readlines()

    i = 0
    if RANDOMIZE:
        i = random.randint(0, len(lines))
    line = lines[i].strip()
    del lines[i]
    vlog(i, line)
    
    if not DRYRUN:
        with codecs.open(fn, 'w', encoding='utf-8') as fp:
            fp.write(''.join(lines))

    return Note(line, line)

# ######################################################## #

def check_paths(ddir, mdir, afn):
    ddir = os.path.realpath(ddir)
    if not os.path.exists(ddir):
        vlog('Invalid input dir/file', ddir, force=True)
        return ('', '', '')

    mdir = os.path.realpath(mdir)
    if not os.path.isdir(mdir):
        vlog('Invalid output directory', mdir, force=True)
        return ('', '', '')

    if afn:
        afn = os.path.realpath(afn)
        if not os.path.isfile(afn):
            vlog('Invalid auth file', afn, force=True)
            return ('', '', '')

    return ddir, mdir, afn

def main(db, mdir, authfn):
    vlog(db, mdir)
    note = None
    if os.path.isdir(db):
        note = pick_from_dir(db)
    elif os.path.isfile(db):
        note = pick_from_file(db)

    vlog(note.text, force=True)
    if authfn and not DRYRUN:
        api = jltw.open_twitter(authfn)
        if note.media:
            with open(note.media, 'rb') as fp:
                api.PostUpdate(note.text, media=fp)
        else:
            api.PostUpdate(note.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('datadir',
            help='Directory containing postit files, OR single file containing lines')
    parser.add_argument('mediadir',
            nargs='?',
            default='',
            help='Directory containing media files')
    parser.add_argument('-r', '--random',
            dest='randomize',
            action='store_true',
            help='choose randomly instead of taking notes in order')
    parser.add_argument('-t', '--tweet',
            dest='tweet',
            action='store',
            type=str,
            default='',
            help='post to twitter, with credentials in given file.')
    parser.add_argument('-n', '--dry-run',
            dest='dryrun',
            action='store_true',
            help='don\'t really do anything')
    parser.add_argument('-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='print debug spam')
    args = parser.parse_args()

    if args.dryrun:
        DRYRUN = True
    if args.verbose:
        VERBOSE = True
    if args.randomize:
        RANDOMIZE = True

    ddir, mdir, afn = check_paths(args.datadir, args.mediadir, args.tweet)
    if not ddir:
        exit(1)

    main(ddir, mdir, afn)

