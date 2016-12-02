from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.setup.sections.jsonsource import JSONSourceSection
from opengever.setup.sections.resolveguid import DuplicateGuid
from opengever.setup.sections.resolveguid import MissingGuid
from opengever.setup.sections.resolveguid import MissingParent
from opengever.setup.sections.resolveguid import ResolveGUIDSection
from opengever.setup.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestResolveGUID(FunctionalTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        transmogrifier = MockTransmogrifier()
        options = {'blueprint', 'opengever.setup.resolveguid'}

        return ResolveGUIDSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(JSONSourceSection))
        verifyClass(ISection, JSONSourceSection)

        self.assertTrue(ISectionBlueprint.providedBy(JSONSourceSection))
        verifyObject(ISectionBlueprint, JSONSourceSection)

    def test_requires_guid(self):
        section = self.setup_section(
            previous=[{'foo': 1234}]
        )

        with self.assertRaises(MissingGuid):
            list(section)

    def test_prevents_duplicate_guid(self):
        section = self.setup_section(
            previous=[{'guid': 1234}, {'guid': 1234}]
        )

        with self.assertRaises(DuplicateGuid):
            list(section)

    def test_validates_parent_guid(self):
        section = self.setup_section(
            previous=[{'guid': 1234, 'parent_guid': 1337}]
        )

        with self.assertRaises(MissingParent):
            list(section)

    def test_reorders_items_parents_before_children(self):
        section = self.setup_section(previous=[
            {'guid': 3, 'parent_guid': 2},
            {'guid': 1337},
            {'guid': 2, 'parent_guid': 1},
            {'guid': 1},
            {'guid': 'qux', 'parent_guid': 1337},
        ])

        self.assertEqual([
                {'guid': 1337},
                {'guid': 'qux', 'parent_guid': 1337},
                {'guid': 1},
                {'guid': 2, 'parent_guid': 1},
                {'guid': 3, 'parent_guid': 2},
            ],
            list(section)
        )

    def test_defines_guid_mapping_on_transmogrifier(self):
        item = {'guid': 'marvin'}
        section = self.setup_section(previous=[item])
        transmogrifier = section.transmogrifier

        list(section)
        self.assertEqual(item, transmogrifier.item_by_guid['marvin'])