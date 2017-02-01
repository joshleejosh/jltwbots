# encoding: utf-8
import os, unittest, tempfile, codecs
import jltw.postit

def writef(fn, s):
    with codecs.open(fn, 'w', encoding='utf-8') as fp:
        fp.write(s)

def rmf(fn):
    if os.path.isfile(fn):
        os.remove(fn)

class PostitTest(unittest.TestCase):
    def setUp(self):
        # make a single file db with one post per line.
        self.testfileContents = u"""I am the first post.
    Hey, I äm the secoñd post?   
Yo, I am OLD ITALIC LETTER UU: 𐌞 omg!
"""
        self.testfiled, self.testfilen = tempfile.mkstemp()
        writef(self.testfilen, self.testfileContents)

        # make a multi file db with one post per file.
        self.testdirn = tempfile.mkdtemp()
        fn = os.path.join(self.testdirn, 'A.postit')
        writef(fn, u"""id:    A  
I am the first post.
""")
        fn = os.path.join(self.testdirn, 'B.postit')
        writef(fn, u'   Hey, I äm the secoñd post?   ')
        self.testmediad, self.testmedian = tempfile.mkstemp()
        writef(self.testmedian, '0') # don't care about contents for unit testing purposes
        fn = os.path.join(self.testdirn, 'C.postit')
        writef(fn, u"""id:C
media:../%s

   Yo, I am OLD ITALIC LETTER UU: 𐌞 omg!
Also, I'm a multiline post!
   

"""%os.path.basename(self.testmedian))

    def tearDown(self):
        rmf(self.testfilen)
        rmf(self.testmedian)
        rmf(os.path.join(self.testdirn, 'C.postit'))
        rmf(os.path.join(self.testdirn, 'B.postit'))
        rmf(os.path.join(self.testdirn, 'A.postit'))
        os.rmdir(self.testdirn)

    def test_fromfile(self):
        note = jltw.postit.pick_from_file(self.testfilen)
        self.assertEqual(note.id, 'I am the first post.')
        self.assertEqual(note.text, 'I am the first post.')
        self.assertEqual(note.filename, '')
        self.assertEqual(note.media, '')

        note = jltw.postit.pick_from_file(self.testfilen)
        self.assertEqual(note.id, u'Hey, I äm the secoñd post?') # strip whitespace off the ends
        self.assertEqual(note.text, u'Hey, I äm the secoñd post?')
        self.assertEqual(note.filename, '')
        self.assertEqual(note.media, '')

        note = jltw.postit.pick_from_file(self.testfilen)
        self.assertEqual(note.id, u'Yo, I am OLD ITALIC LETTER UU: 𐌞 omg!')
        self.assertEqual(note.text, u'Yo, I am OLD ITALIC LETTER UU: 𐌞 omg!')
        self.assertEqual(note.filename, '')
        self.assertEqual(note.media, '')

        try:
            note = jltw.postit.pick_from_file(self.testfilen)
            self.fail('no lines left in file?')
        except IndexError:
            pass
        except Exception as e:
            self.fail('unexpected exception %s'%e)

    def test_fromdir(self):
        note = jltw.postit.pick_from_dir(self.testdirn)
        self.assertEqual(note.id, 'A')
        self.assertEqual(note.text, u'I am the first post.')
        self.assertEqual(note.filename, os.path.realpath(os.path.join(self.testdirn, 'A.postit')))
        self.assertEqual(note.media, '')

        # No ID in the file, get it from the filename.
        note = jltw.postit.pick_from_dir(self.testdirn)
        self.assertEqual(note.id, 'B')
        self.assertEqual(note.text, u'Hey, I äm the secoñd post?')
        self.assertEqual(note.filename, os.path.realpath(os.path.join(self.testdirn, 'B.postit')))
        self.assertEqual(note.media, '')

        # multiline post with media
        note = jltw.postit.pick_from_dir(self.testdirn)
        self.assertEqual(note.id, 'C')
        self.assertEqual(note.text, u'Yo, I am OLD ITALIC LETTER UU: 𐌞 omg!\nAlso, I\'m a multiline post!')
        self.assertEqual(note.filename, os.path.realpath(os.path.join(self.testdirn, 'C.postit')))
        self.assertEqual(note.media, os.path.realpath(self.testmedian))

        try:
            note = jltw.postit.pick_from_dir(self.testdirn)
            self.fail('no files left?')
        except IndexError:
            pass
        except Exception as e:
            self.fail('unexpected exception %s'%e)

