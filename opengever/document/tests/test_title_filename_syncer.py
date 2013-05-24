from opengever.testing import Builder
from opengever.testing import FunctionalTestCase


class TestTitleFilenameSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestTitleFilenameSyncer, self).setUp()

    def test_infer_title_from_filename(self):
        document = Builder("document") \
            .attach_file_containing(u"blup", name=u'T\xf6st.txt').create()
        self.assertEqual(document.title, u'T\xf6st')
        self.assertEqual(document.file.filename, u'tost.txt')

    def test_infer_filename_from_title(self):
        document = Builder("document") \
            .titled("My Title") \
            .attach_file_containing(u"blup", name=u"wrong.txt").create()
        self.assertEqual(document.title, u'My Title')
        self.assertEqual(document.file.filename, u'my-title.txt')
