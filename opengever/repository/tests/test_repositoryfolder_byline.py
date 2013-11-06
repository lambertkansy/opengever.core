from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.classification import PRIVACY_LAYER_NO
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestRepositoryfolderByline(TestBylineBase):

    def setUp(self):
        super(TestRepositoryfolderByline, self).setUp()

        self.intids = getUtility(IIntIds)

        create_ogds_user('hugo.boss')

        self.repo = create(Builder('repository')
               .in_state('repositoryfolder-state-active')
               .having(privacy_layer=PRIVACY_LAYER_NO))

        self.browser.open(self.repo.absolute_url())

    def test_dossier_byline_icon_display(self):
        icon = self.get_byline_element_by_class('byline-icon')
        self.assertEquals('byline-icon contenttype-opengever-repository-repositoryfolder',
                          icon.target.get('class'))

    def test_repository_byline_privacy_layer_display(self):
        responsible = self.get_byline_element_by_class('privacy_layer').getchildren()[0]
        self.assertEquals('privacy_layer_no', responsible.text_content())

    def test_repository_byline_public_trial_display(self):
        public_trial = self.get_byline_value_by_label('Public Trial:')
        self.assertEquals('unchecked', public_trial.text_content())
