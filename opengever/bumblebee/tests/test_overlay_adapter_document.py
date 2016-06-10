from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testbrowser import browsing
from opengever.bumblebee.browser.overlay import BumblebeeBaseDocumentOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_get_overlay_adapter_for_documents(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsInstance(adapter, BumblebeeBaseDocumentOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeBaseDocumentOverlay)


class TestGetPreviewPdfUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_preview_pdf_url_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIn('not_digitally_available.png', adapter.get_preview_pdf_url())


class TestGetOpenAsPdfLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_pdf_url_as_string(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIn(
            '/YnVtYmxlYmVl/api/v3/resource/', adapter.get_open_as_pdf_url())

    def test_returns_none_if_no_mimetype_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_open_as_pdf_url())

    def test_returns_none_if_mimetype_is_not_supported(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              "data", name=u"test.notsupported"))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_open_as_pdf_url())


class TestGetPdfFilename(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_changes_filename_extension_to_pdf_and_returns_filename(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              "data", name=u"test.docx"))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual('testdokumant.docx', document.file.filename)
        self.assertEqual('testdokumant.pdf', adapter._get_pdf_filename())

    def test_returns_none_if_no_file_is_given(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter._get_pdf_filename())


class TestGetFileTitle(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_file_title_if_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .titled('Example')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual('example.docx', adapter.get_file_title())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_file_title())


class TestGetFileSize(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_file_size_in_kb_if_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(26, adapter.get_file_size())

    def test_returns_none_if_no_file_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_file_size())


class TestGetCreator(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_link_to_creator(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)
        creator_link = adapter.get_creator_link()

        self.assertIn('Test User (test_user_1_)', creator_link)
        self.assertIn('http://nohost/plone/@@user-details/test_user_1_',
                      creator_link)


class TestGetDocumentDate(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_localized_document_date(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(u'Jan 01, 2014', adapter.get_document_date())

    def test_returns_none_if_no_document_date_is_set(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=''))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_document_date())


class TestGetContainingDossier(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_the_containing_dossier(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .having(document_date=date(2014, 1, 1)))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(dossier, adapter.get_containing_dossier())


class TestGetSequenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_sequence_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(1, adapter.get_sequence_number())


class TestGetReferenceNumber(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_reference_number(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual('Client1 / 1 / 1', adapter.get_reference_number())


class TestGetCheckoutLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_checkout_and_edit_url(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            adapter.get_checkout_url())

    def test_returns_none_if_no_document_is_available_to_checkout(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(None, adapter.get_checkout_url())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))
        create(Builder('user')
               .with_userid('bond')
               .with_roles('Member', 'Reader'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIn(
            'http://nohost/plone/dossier-1/document-1/editing_document',
            adapter.get_checkout_url())

        login(self.portal, 'bond')
        self.assertIsNone(None, adapter.get_checkout_url())


class TestGetDownloadCopyLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_returns_download_copy_link_as_html_link(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        browser.open_html(adapter.get_download_copy_link())

        self.assertEqual('Download copy', browser.css('a').first.text)

    def test_returns_none_if_no_document_is_available(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)
        self.assertIsNone(adapter.get_download_copy_link())


class TestGetEditMetadataLink(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_edit_metadata_url(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            adapter.get_edit_metadata_url())

    def test_returns_none_if_user_is_not_allowed_to_edit(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        create(Builder('user')
               .with_userid('bond')
               .with_roles('Member', 'Reader'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/edit',
            adapter.get_edit_metadata_url())

        login(self.portal, 'bond')
        self.assertIsNone(adapter.get_edit_metadata_url())


class TestHasFile(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_true_if_document_has_a_file(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertTrue(adapter.has_file())

    def test_returns_false_if_document_has_no_file(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertFalse(adapter.has_file())


class TestGetFile(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_none_if_document_has_no_file(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_file())

    def test_returns_file_if_document_has_file(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertEqual(document.file, adapter.get_file())