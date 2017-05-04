from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from zExceptions import Unauthorized
import urllib


class TestRequireLoginScript(FunctionalTestCase):

    def setUp(self):
        super(TestRequireLoginScript, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())

    @browsing
    def test_require_login_redirects_to_came_from_if_already_logged_in(self, browser):
        browser.login().open(
            view='require_login?came_from={}'.format(
                urllib.quote(self.document.absolute_url())))
        self.assertEqual(self.document.absolute_url(),
                         browser.url.split('?')[0])

    @browsing
    def test_require_login_displays_login_form_and_redirecs_upon_login(self, browser):
        browser.open(
            view='require_login?came_from={}'.format(
                urllib.quote(self.document.absolute_url())))
        self.assertTrue(
            browser.url.startswith('http://nohost/plone/require_login'),
            'Unexpected URL {}'.format(browser.url))

        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertEqual(self.document.absolute_url(), browser.url)

    @browsing
    def test_unauthorized_visible_when_raised_in_traversal(self, browser):
        with self.assertRaises(Unauthorized):
            browser.login().open(view='test-traversal-unauthorized')

    @browsing
    def test_unauthorized_visible_when_raised_in_publishing(self, browser):
        browser.replace_request_header('X-zope-handle-errors', 'True')
        browser.login().open(view='test-publishing-unauthorized')
        self.assertEquals('Insufficient Privileges', plone.first_heading())
