from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


class TestLocalRolesSetter(FunctionalTestCase):

    def test_local_roles_setter(self):
        portal = self.portal

        # Local roles setter
        # ==================
        # The local roles setter sets roles on a created or modified task,
        # on every related item and on the next parent which has a defferent
        # portal type (usually the dossier).
        intids = getUtility(IIntIds)

        create_client('plone', group='og_mandant1_users',
                      inbox_group=u'og_mandant1_inbox')
        create_client('client2', group='og_mandant2_users',
                      inbox_group=u'og_mandant2_inbox')
        set_current_client_id(portal, 'plone')
        create_ogds_user(TEST_USER_ID,
                         groups=(u'og_mandant1_users',
                                 u'og_mandant1_inbox',
                                 u'og_mandant2_users'))

        # Lets assume we have a related item. For simplicity we also create
        # a task, since tasks are the only dexterity type we now for shure
        # we should have it here:
        folder = portal['Members'][TEST_USER_ID]
        related = createContentInContainer(
                 folder, 'opengever.task.task',
                 title=u'Related',
                 checkConstraints=False,
                 responsible_client="plone")

        self.assertEquals(
            (('test_user_1_', ('Owner',)),),
            related.get_local_roles())

        # Let's also check the local roles on the folder,
        # which is our container and acts like a dossier:
        self.assertEquals(
            (('test_user_1_', ('Owner',)),),
            folder.get_local_roles())

        # Now let's create a new task with a relation to our "related" task:
        relation = RelationValue(intids.getId(related))
        task2 = createContentInContainer(
                 folder, 'opengever.task.task',
                 checkConstraints=False,
                 task_type=u'direct-execution',
                 title=u'Task 2', responsible=u'foo',
                 responsible_client="plone",
                 relatedItems=[relation])

        # Now check the local roles:
        self.assertEquals(
            (('foo', ('Editor',)),
             (u'og_mandant1_inbox', ('Editor',)),
             ('test_user_1_', ('Owner',))),
            task2.get_local_roles())

        self.assertEquals(
            (('foo', ('Contributor',)),
             (u'og_mandant1_inbox', ('Contributor',)),
             ('test_user_1_', ('Owner',))),
            folder.get_local_roles())

        self.assertEquals(
            (('foo', ('Reader',)),
             (u'og_mandant1_inbox', ('Reader',)),
             ('test_user_1_', ('Owner',))),
            related.get_local_roles())

        # Now lets create a new task with a task type
        # from bidirectional_by_reference,
        # which should set Editor role on the related item:
        relation2 = RelationValue(intids.getId(related))
        task3 = createContentInContainer(
                 folder, 'opengever.task.task',
                 checkConstraints=False,
                 task_type=u'comment',
                 title=u'Task 3', responsible=u'bar',
                 responsible_client="client2",
                 relatedItems=[relation2])

        self.assertEquals(
            (('bar', ('Editor',)),
             (u'og_mandant2_inbox', ('Editor',)),
             ('test_user_1_', ('Owner',))),
            task3.get_local_roles()
        )

        self.assertEquals(
            (('bar', ('Contributor',)),
             ('foo', ('Contributor',)),
             (u'og_mandant1_inbox', ('Contributor',)),
             (u'og_mandant2_inbox', ('Contributor',)),
             ('test_user_1_', ('Owner',))),
            folder.get_local_roles())

        self.assertEquals(
            (('bar', ('Editor', 'Reader')),
             ('foo', ('Reader',)),
             (u'og_mandant1_inbox', ('Reader',)),
             (u'og_mandant2_inbox', ('Editor', 'Reader')),
             ('test_user_1_', ('Owner',))),
            related.get_local_roles())

        # When updating, it should also update the related items:
        task3.responsible = u'new'
        task3.responsible_client = u'plone'
        notify(ObjectModifiedEvent(task3))

        self.assertEquals(
            (('bar', ('Editor',)),
             ('new', ('Editor',)),
             (u'og_mandant1_inbox', ('Editor',)),
             (u'og_mandant2_inbox', ('Editor',)),
             ('test_user_1_', ('Owner',))),
            task3.get_local_roles())

        self.assertEquals(
            (('bar', ('Contributor',)),
             ('foo', ('Contributor',)),
             ('new', ('Contributor',)),
             (u'og_mandant1_inbox', ('Contributor',)),
             (u'og_mandant2_inbox', ('Contributor',)),
             ('test_user_1_', ('Owner',))),
            folder.get_local_roles())

        self.assertEquals(
            (('bar', ('Editor', 'Reader')),
             ('foo', ('Reader',)),
             ('new', ('Editor', 'Reader')),
             (u'og_mandant1_inbox', ('Editor', 'Reader')),
             (u'og_mandant2_inbox', ('Editor', 'Reader')),
             ('test_user_1_', ('Owner',))),
            related.get_local_roles()
        )

        # TODO: Missing test: we should also test here that if we select a inbox
        # it also tests that the group of the client (client.group) is used for
        # setting local roles and not the actual value. But we have to setup ogds
        # for that
