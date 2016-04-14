from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import obj2paths
from plone.protect import createToken


class TestDisposition(FunctionalTestCase):

    def setUp(self):
        super(TestDisposition, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier').within(self.repository))
        self.dossier2 = create(Builder('dossier').within(self.repository))
        self.dossier3 = create(Builder('dossier').within(self.repository))

    def test_id_is_sequence_number_prefixed_with_disposition(self):
        disposition_1 = create(Builder('disposition'))
        disposition_2 = create(Builder('disposition'))

        self.assertEquals('disposition-1', disposition_1.getId())
        self.assertEquals('disposition-2', disposition_2.getId())

    def test_title_is_sequence_number_prefixed_with_Disposition_and_space(self):
        disposition = create(Builder('disposition'))

        self.assertEquals(u'Disposition 1', disposition.title)
        self.assertEquals('Disposition 1', disposition.Title())
        self.assertEquals(u'Disposition 1', obj2brain(disposition).Title)

    @browsing
    def test_can_be_added(self, browser):
        browser.login().open(self.root)
        factoriesmenu.add('Disposition')
        browser.fill({'Reference': 'Ablieferung X29238',
                      'Dossiers': [self.dossier1, self.dossier2]})
        browser.find('Save').click()

        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_selected_dossiers_in_the_list_are_preselected(self, browser):
        data = {'paths:list': obj2paths([self.dossier1, self.dossier3]),
                '_authenticator': createToken()}
        browser.login().open(self.root,
                             view='++add++opengever.disposition.disposition',
                             data=data)

        browser.fill({'Reference': 'Ablieferung X29238'})
        browser.find('Save').click()

        self.assertEquals([self.dossier1, self.dossier3],
                          [rel.to_object for rel in browser.context.dossiers])