from grokcore.component.testing import grok
from mocker import ANY
from opengever.dossier.behaviors.participation import ParticipationHandler
from opengever.dossier.interfaces import IParticipationCreated, IParticipationRemoved
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.mocktestcase import MockTestCase
from z3c.form.testing import TestRequest
from zope.annotation.interfaces import IAnnotations
from zope.component import provideUtility
from zope.interface import Interface
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import transaction
import unittest2 as unittest


class TestParticipationHanlder(MockTestCase):

    def setUp(self):
        grok('opengever.dossier.behaviors.participation')
        self.context = self.mocker.mock()

        #annotation mock
        annonation_storage = {}
        annotation_adapter = lambda obj: annonation_storage
        self.mock_adapter(annotation_adapter, IAnnotations, [Interface, ])

        created_handler = self.mocker.mock()
        self.expect(created_handler(ANY)).result('created event fired').count(0, 3)
        self.mock_handler(created_handler, [IParticipationCreated,])

        removed_handler = self.mocker.mock()
        self.expect(removed_handler(ANY)).result('removed event fired').count(0,1)
        self.mock_handler(removed_handler, [IParticipationRemoved,])

    def test_participation_with_handler(self):
        self.replay()
        handler = ParticipationHandler(self.context)

        # creation
        peter = handler.create_participation(
            {'contact':'peter', 'roles':['Reader',],})
        sepp = handler.create_participation(
            {'contact':'sepp', 'roles':['Reader','Editor'],})
        hugo = handler.create_participation(
            {'contact':'hugo'})

        # test appending
        handler.append_participiation(peter)
        self.assertEquals(handler.get_participations(), [peter,])

        handler.append_participiation(sepp)
        self.assertEquals(handler.get_participations(), [peter, sepp])

        # an existing participation should not be addable multiple time
        self.assertEquals(handler.append_participiation(peter), None)

        # test has participation
        self.assertEquals(handler.has_participation(peter), True)
        self.assertEquals(handler.has_participation(hugo), False)

        # test removing
        handler.remove_participation(peter)
        self.assertEquals(handler.get_participations(), [sepp,])
