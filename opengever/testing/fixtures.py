from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from contextlib import nested
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import ticking_creator
from ftw.testing import freeze
from ftw.testing import staticuid
from functools import wraps
from opengever.base.command import CreateEmailCommand
from opengever.base.model import create_session
from opengever.mail.tests import MAIL_DATA
from opengever.meeting.proposalhistory import BaseHistoryRecord
from opengever.ogds.base.utils import ogds_service
from opengever.testing import assets
from opengever.testing.integration_test_case import FEATURE_FLAGS
from operator import methodcaller
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from time import time
from zope.component.hooks import getSite
import logging
import pytz


class OpengeverContentFixture(object):
    """Provide a basic content fixture for integration tests."""

    def __init__(self):
        start = time()
        self._logger = logger = logging.getLogger('opengever.testing')
        self._lookup_table = {
            'manager': ('user', SITE_OWNER_NAME)}

        with self.freeze_at_hour(6):
            self.create_units()

        with self.freeze_at_hour(7):
            self.create_users()
            self.create_teams()
            self.create_contacts()

        with self.freeze_at_hour(8):
            with self.login(self.administrator):
                self.create_repository_tree()
                self.create_templates()
                with self.features('meeting'):
                    self.create_committees()

        with self.freeze_at_hour(14):
            with self.login(self.dossier_responsible):
                self.create_treaty_dossiers()
                self.create_empty_dossier()

        with self.freeze_at_hour(15):
            with self.login(self.dossier_responsible):
                self.create_emails()

        with self.freeze_at_hour(16):
            with self.login(self.committee_responsible):
                self.create_meetings()

        logger.info('(fixture setup in %ds) ', round(time() - start, 3))

    def __call__(self):
        return self._lookup_table

    def create_units(self):
        self.admin_unit = create(
            Builder('admin_unit')
            .having(title=u'Hauptmandant',
                    unit_id=u'plone',
                    public_url='http://nohost/plone')
            .as_current_admin_unit())

        self.org_unit = create(
            Builder('org_unit')
            .id('fa')
            .having(title=u'Finanzamt',
                    admin_unit=self.admin_unit)
            .with_default_groups()
            .as_current_org_unit())

    def create_users(self):
        self.administrator = self.create_user(
            'administrator', u'Nicole', u'Kohler',
            ['Administrator', 'APIUser'])
        self.dossier_responsible = self.create_user(
            'dossier_responsible', u'Robert', u'Ziegler')
        self.regular_user = self.create_user(
            'regular_user', u'K\xe4thi', u'B\xe4rfuss')
        self.meeting_user = self.create_user(
            'meeting_user', u'Herbert', u'J\xe4ger')
        self.secretariat_user = self.create_user(
            'secretariat_user', u'J\xfcrgen', u'K\xf6nig',
            group=self.org_unit.inbox_group)
        self.committee_responsible = self.create_user(
            'committee_responsible', u'Fr\xe4nzi', u'M\xfcller')

    def create_teams(self):
        users = [ogds_service().find_user(user.getId())
                 for user in [self.regular_user, self.dossier_responsible]]
        group_a = create(Builder('ogds_group')
                         .having(groupid='projekt_a',
                                 title=u'Projekt A', users=users))
        self.projekt_a = create(
            Builder('ogds_team')
            .having(title=u'Projekt \xdcberbaung Dorfmatte',
                    group=group_a, org_unit=self.org_unit))

        users = [ogds_service().find_user(user.getId())
                 for user in [self.committee_responsible, self.meeting_user]]
        group_b = create(Builder('ogds_group')
                         .having(groupid='projekt_b',
                                 title=u'Projekt B', users=users))
        self.projekt_b = create(
            Builder('ogds_team')
            .having(title=u'Sekretariat Abteilung XY',
                    group=group_b, org_unit=self.org_unit))

    @staticuid()
    def create_repository_tree(self):
        self.root = self.register('repository_root', create(
            Builder('repository_root')
            .having(title_de=u'Ordnungssystem',
                    title_fr=u'Syst\xe8me de classement')))
        self.root.manage_setLocalRoles(self.org_unit.users_group_id,
                                       ('Reader', 'Contributor', 'Editor'))
        self.root.manage_setLocalRoles(self.secretariat_user.getId(),
                                       ('Reviewer', 'Publisher'))
        self.root.reindexObjectSecurity()

        self.repofolder0 = self.register('branch_repofolder', create(
            Builder('repository').within(self.root)
            .having(title_de=u'F\xfchrung',
                    title_fr=u'Direction',
                    description=u'Alles zum Thema F\xfchrung.')))

        self.repofolder00 = self.register('leaf_repofolder', create(
            Builder('repository').within(self.repofolder0)
            .having(title_de=u'Vertr\xe4ge und Vereinbarungen',
                    title_fr=u'Contrats et accords')))

        self.repofolder1 = self.register('empty_repofolder', create(
            Builder('repository').within(self.root)
            .having(title_de=u'Rechnungspr\xfcfungskommission',
                    title_fr=u'Commission de v\xe9rification')))

    @staticuid()
    def create_contacts(self):
        self.contactfolder = self.register('contactfolder', create(
            Builder('contactfolder')
            .titled(u'Kontakte')
            .having(id='kontakte')))

        self.contactfolder.manage_setLocalRoles(
            self.org_unit.users_group_id, ('Reader',))
        self.contactfolder.manage_setLocalRoles(
            self.org_unit.users_group_id, ('Reader', 'Contributor', 'Editor'))
        self.contactfolder.reindexObjectSecurity()

        self.hanspeter_duerr = self.register('hanspeter_duerr', create(
            Builder('contact')
            .within(self.contactfolder)
            .having(firstname=u'Hanspeter',
                    lastname='D\xc3\xbcrr'.decode('utf-8'))))

        self.franz_meier = self.register('franz_meier', create(
            Builder('contact')
            .within(self.contactfolder)
            .having(firstname=u'Franz', lastname=u'Meier',
                    email=u'meier.f@example.com')))

        self.josef_buehler = create(
            Builder('person')
            .having(firstname=u'Josef', lastname=u'B\xfchler'))

        self.meier_ag = create(Builder('organization').named(u'Meier AG'))
        create_session().flush()

    @staticuid()
    def create_templates(self):
        templates = self.register('templates', create(
            Builder('templatefolder')
            .titled(u'Vorlagen')
            .having(id='vorlagen')))
        templates.manage_setLocalRoles(self.org_unit.users_group_id,
                                       ('Reader',))
        templates.reindexObjectSecurity()

        self.sablon_template = self.register('sablon_template', create(
            Builder('sablontemplate')
            .within(templates)
            .with_asset_file('sablon_template.docx')))

        with self.features('meeting', 'word-meeting'):
            self.proposal_template = self.register('proposal_template', create(
                Builder('proposaltemplate')
                .titled(u'Geb\xfchren')
                .with_asset_file(u'vertragsentwurf.docx')
                .within(templates)))

    @staticuid()
    def create_committees(self):
        self.committee_container = self.register('committee_container', create(
            Builder('committee_container')
            .titled(u'Sitzungen')
            .having(
                ad_hoc_template=self.proposal_template,
                agendaitem_list_template=self.sablon_template,
                excerpt_template=self.sablon_template,
                protocol_template=self.sablon_template,
                paragraph_template=self.sablon_template,
                )
            ))
        self.committee_container.manage_setLocalRoles(
            self.committee_responsible.getId(), ('MeetingUser',))
        self.committee_container.manage_setLocalRoles(
            self.meeting_user.getId(), ('MeetingUser',))
        self.committee_container.manage_setLocalRoles(
            self.administrator.getId(), ('CommitteeAdministrator',))
        self.committee_container.reindexObjectSecurity()

        self.committee = self.register('committee', self.create_committee(
            title=u'Rechnungspr\xfcfungskommission',
            repository_folder=self.repofolder1,
            group_id='committee_rpk_group',
            responsibles=[self.administrator,
                          self.committee_responsible]))
        self.register_raw('committee_id', self.committee.load_model().committee_id)
        self.committee.manage_setLocalRoles(
            self.meeting_user.getId(), ('CommitteeMember',))

        self.committee_president = self.create_committee_membership(
            self.committee,
            'committee_president',
            firstname=u'Heidrun',
            lastname=u'Sch\xf6ller',
            email='h.schoeller@web.de',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31))

        self.committee_secretary = self.create_committee_membership(
            self.committee,
            'committee_secretary',
            firstname=u'Henning',
            lastname=u'M\xfcller',
            email='h.mueller@gmx.ch',
            date_from=datetime(2016, 1, 1),
            date_to=datetime(2016, 12, 31))

        self.committee_participant_1 = self.create_committee_membership(
            self.committee,
            'committee_participant_1',
            firstname=u'Gerda',
            lastname=u'W\xf6lfl',
            email='g.woelfl@hotmail.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31))

        self.committee_participant_2 = self.create_committee_membership(
            self.committee,
            'committee_participant_2',
            firstname=u'Jens',
            lastname=u'Wendler',
            email='jens-wendler@gmail.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31))

        self.empty_committee = self.register(
            'empty_committee', self.create_committee(
                title=u'Kommission f\xfcr Verkehr',
                repository_folder=self.repofolder1,
                group_id='committee_ver_group',
                responsibles=[self.administrator,
                              self.committee_responsible]))
        self.register_raw('empty_committee_id',
                          self.empty_committee.load_model().committee_id)
        self.empty_committee.manage_setLocalRoles(
            self.meeting_user.getId(), ('CommitteeMember',))

    @staticuid()
    def create_treaty_dossiers(self):
        self.dossier = self.register('dossier', create(
            Builder('dossier').within(self.repofolder00)
            .titled(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .having(description=u'Alle aktuellen Vertr\xe4ge mit der'
                    u' kantonalen Finanzverwaltung sind hier abzulegen.'
                    u' Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2016, 1, 1),
                    responsible='hugo.boss')))

        create(Builder('contact_participation')
               .for_contact(self.meier_ag)
               .for_dossier(self.dossier)
               .with_roles(['final-drawing']))

        create(Builder('contact_participation')
               .for_contact(self.josef_buehler)
               .for_dossier(self.dossier)
               .with_roles(['final-drawing', 'participation']))

        document = self.register('document', create(
            Builder('document').within(self.dossier)
            .titled(u'Vertr\xe4gsentwurf')
            .with_asset_file('vertragsentwurf.docx')))

        task = self.register('task', create(
            Builder('task').within(self.dossier)
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='correction',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-in-progress')
            .relate_to(document)))

        self.register('subtask', create(
            Builder('task').within(task)
            .titled(u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='correction',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-resolved')
            .relate_to(document)))

        self.register('taskdocument', create(
            Builder('document').within(task)
            .titled(u'Feedback zum Vertragsentwurf')
            .attach_file_containing('Feedback text',
                                    u'vertr\xe4g sentwurf.docx')))

        proposal = self.register('proposal', create(
            Builder('proposal').within(self.dossier)
            .having(title=u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen',
                    committee=self.committee.load_model())
            .relate_to(document)
            .as_submitted()))
        self.register_path(
            'submitted_proposal',
            proposal.load_model().submitted_physical_path.encode('utf-8'))

        self.register('draft_proposal', create(
            Builder('proposal').within(self.dossier)
            .having(title=u'Antrag f\xfcr Kreiselbau',
                    committee=self.empty_committee.load_model())))

        self.decided_proposal = create(
                Builder('proposal').within(self.dossier)
                .having(title=u'Initialvertrag f\xfcr Bearbeitung',
                        committee=self.committee.load_model())
                .as_submitted())
        self.register_path(
            'decided_proposal',
            self.decided_proposal.load_model().submitted_physical_path.encode('utf-8'))

        with self.features('meeting', 'word-meeting'):
            word_proposal = self.register('word_proposal', create(
                Builder('proposal').within(self.dossier)
                .having(title=u'\xc4nderungen am Personalreglement',
                        committee=self.committee.load_model())
                .relate_to(document)
                .with_proposal_file(assets.load('vertragsentwurf.docx'))
                .as_submitted()))
            self.register_path(
                'submitted_word_proposal',
                word_proposal.load_model().submitted_physical_path.encode('utf-8'))

            self.register('draft_word_proposal', create(
                Builder('proposal').within(self.dossier)
                .having(title=u'\xdcberarbeitung der GAV',
                        committee=self.empty_committee.load_model())))

        subdossier = self.register('subdossier', create(
            Builder('dossier').within(self.dossier).titled(u'2016')))

        self.register('subdossier2', create(
            Builder('dossier').within(self.dossier).titled(u'2015')))

        self.register('subdocument', create(
            Builder('document').within(subdossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge von 2016')
            .attach_file_containing('Excel dummy content', u'tab\xe4lle.xlsx')))

        self.register('archive_dossier', create(
            Builder('dossier').within(self.repofolder00)
            .titled(u'Archiv Vertr\xe4ge')
            .having(description=u'Archiv der Vertr\xe4ge vor 2016.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2000, 1, 1),
                    end=date(2015, 12, 31),
                    responsible='hugo.boss')
            .in_state('dossier-state-resolved')))

    @staticuid()
    def create_empty_dossier(self):
        self.register('empty_dossier', create(
            Builder('dossier').within(self.repofolder00)
            .titled(u'An empty dossier')
            .having(start=date(2016, 1, 1),
                    responsible='hugo.boss')))

    @staticuid()
    def create_emails(self):
        self.mail_eml = self.register('mail_eml', create(
            Builder("mail")
            .with_message(MAIL_DATA)
            .within(self.dossier)))
        self.register('mail', self.mail_eml)

        class MockMsg2MimeTransform(object):

            def transform(self, data):
                return 'mock-eml-body'

        command = CreateEmailCommand(self.dossier,
                                     'testm\xc3\xa4il.msg',
                                     'mock-msg-body',
                                     transform=MockMsg2MimeTransform())
        self.mail_msg = self.register('mail_msg', command.execute())

    @staticuid()
    def create_meetings(self):
        meeting_dossier = self.register('meeting_dossier', create(
            Builder('meeting_dossier').within(self.repofolder00)
            .titled(u'Sitzungsdossier 9/2017')
            .having(start=date(2016, 9, 12),
                    relatedDossier=[self.dossier],
                    responsible=self.committee_responsible.getId())))
        self.meeting = create(
            Builder('meeting')
            .having(title=u'9. Sitzung der Rechnungspr\xfcfungskommission',
                    committee=self.committee.load_model(),
                    location=u'B\xfcren an der Aare',
                    start=datetime(2016, 9, 12, 15, 30, tzinfo=pytz.UTC),
                    end=datetime(2016, 9, 12, 17, 0, tzinfo=pytz.UTC),
                    presidency=self.committee_president,
                    secretary=self.committee_secretary,
                    participants=[self.committee_participant_1,
                                  self.committee_participant_2])
            .link_with(meeting_dossier))
        create_session().flush()  # trigger id generation, part of path
        self.register_path(
            'meeting', self.meeting.physical_path.encode('utf-8'))

        decided_meeting_dossier = self.register(
            'decided_meeting_dossier', create(
                Builder('meeting_dossier').within(self.repofolder00)
                .titled(u'Sitzungsdossier 8/2017')
                .having(start=date(2016, 8, 17),
                        responsible=self.committee_responsible.getId())))
        self.decided_meeting = create(
            Builder('meeting')
            .having(title=u'8. Sitzung der Rechnungspr\xfcfungskommission',
                    committee=self.committee.load_model(),
                    location=u'B\xfcren an der Aare',
                    start=datetime(2016, 7, 17, 15, 30, tzinfo=pytz.UTC),
                    end=datetime(2016, 7, 17, 16, 30, tzinfo=pytz.UTC),
                    presidency=self.committee_president,
                    secretary=self.committee_secretary,
                    participants=[self.committee_participant_1,
                                  self.committee_participant_2])
            .link_with(decided_meeting_dossier))
        create_session().flush()  # trigger id generation, part of path
        self.register_path(
            'decided_meeting',
            self.decided_meeting.physical_path.encode('utf-8'))

        self.decided_meeting.schedule_proposal(
            self.decided_proposal.load_model())
        self.decided_meeting.close()

    @contextmanager
    def freeze_at_hour(self, hour):
        """Freeze the time when creating content with builders, so that
        we can rely on consistent creation times.
        Since we can sort consistently when all objects have the exact same
        creation times we need to move the clock forward whenever things are
        created, using ftw.builder's ticking creator in combination with a
        frozen clock.

        In order to be able to insert new objects in the fixture without
        mixing up all timestamps, we group the builders and let each group
        start at a given hour, moving the clock two minutes for each builder.
        We move it two minutes because the catalog rounds times sometimes to
        minute precision and we want to be more precise.
        """
        with freeze(datetime(2016, 8, 31, hour, 1, 33, tzinfo=pytz.UTC)) as clock:
            with ticking_creator(clock, minutes=2):
                with self.ticking_proposal_history(clock, seconds=1):
                    yield

    @contextmanager
    def ticking_proposal_history(self, clock, **forward):
        """The proposal history entries must be unique.
        This context manager applies patches so that creating a proposal
        history record will move the freezed clock forward a bit.
        This context manager must not be nested.
        """
        marker_name = '_fixture_patched'

        if getattr(BaseHistoryRecord, marker_name, None):
            yield
            return

        original_init = BaseHistoryRecord.__init__

        @wraps(original_init)
        def patched_init(*args, **kwargs):
            result = original_init(*args, **kwargs)
            clock.forward(**forward)
            return result

        BaseHistoryRecord.__init__ = patched_init
        setattr(BaseHistoryRecord, marker_name, True)
        try:
            yield
        finally:
            BaseHistoryRecord.__init__ = original_init
            delattr(BaseHistoryRecord, marker_name)

    def register(self, attrname, obj):
        """Add an object to the lookup table so that it can be accessed from
        within the name under the attribute with name ``attrname``.
        Return the object for chaining convenience.
        """
        self.register_path(attrname, '/'.join(obj.getPhysicalPath()))
        return obj

    def register_path(self, attrname, path):
        """Add an object to the lookup table by path.
        """
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        if path.startswith(portal_path):
            path = path[len(portal_path):].lstrip('/')
        self._lookup_table[attrname] = ('object', path)

    def register_url(self, attrname, url):
        """Add an object to the lookup table by url.

        The url can be generated based on the `public_url` of the
        `AdminUnit` used for testing.

        It can also be generated by calling `absolute_url` on a plone content
        type.
        """
        if url.startswith(self.admin_unit.public_url):
            url = url[len(self.admin_unit.public_url):]
        elif url.startswith(api.portal.get().absolute_url()):
            url = url[len(api.portal.get().absolute_url()):]
        url = url.lstrip('/')  # sanitize
        self.register_path(attrname, url)

    def register_raw(self, attrname, value):
        """Register a raw value in the lookup table for later lookup.
        The value must be JSON compatible.
        """
        self._lookup_table[attrname] = ('raw', value)

    def create_user(self, attrname, firstname, lastname, globalroles=(), group=None):
        """Create an OGDS user and a Plone user.
        The user is member of the current org unit user group.
        The ``attrname`` is the attribute name used to access this user
        from within tests.
        """
        globalroles = ['Member'] + list(globalroles)
        builder = (
            Builder('user')
            .named(firstname, lastname)
            .with_roles(*globalroles)
            .in_groups(self.org_unit.users_group_id))

        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(Builder('ogds_user')
               .id(plone_user.getId())
               .having(firstname=firstname, lastname=lastname, email=email)
               .assign_to_org_units([self.org_unit])
               .in_group(group))

        self._lookup_table[attrname] = ('user', plone_user.getId())
        return plone_user

    def create_committee_membership(self,
                                    committee,
                                    member_id_register_name,
                                    firstname,
                                    lastname,
                                    email,
                                    date_from,
                                    date_to):
        member = create(
            Builder('member')
            .having(firstname=firstname, lastname=lastname, email=email))

        create(Builder('membership')
               .having(committee=committee,
                       member=member,
                       date_from=date_from,
                       date_to=date_to))
        create_session().flush()  # trigger id generation, part of path

        self.register_url(
            member_id_register_name,
            member.get_url(self.committee_container).encode('utf-8'))
        return member

    def create_committee(self, title, repository_folder, group_id,
                         responsibles):
        # XXX I would have expected the commitee builder to do all of that.
        ogds_members = map(ogds_service().find_user,
                           map(methodcaller('getId'), responsibles))

        create(Builder('ogds_group')
               .having(groupid=group_id,
                       users=ogds_members))
        create(Builder('group')
               .with_groupid(group_id)
               .with_members(*responsibles))
        committee = create(
            Builder('committee')
            .titled(title)
            .within(self.committee_container)
            .having(repository_folder=repository_folder,
                    group_id=group_id))
        return committee

    @contextmanager
    def login(self, user):
        old_manager = getSecurityManager()
        try:
            login(getSite(), user.getId())
            yield
        finally:
            setSecurityManager(old_manager)

    @contextmanager
    def feature(self, feature):
        if feature not in FEATURE_FLAGS:
            raise ValueError('Invalid {!r}'.format(feature))

        before = api.portal.get_registry_record(FEATURE_FLAGS[feature])
        api.portal.set_registry_record(FEATURE_FLAGS[feature], True)
        try:
            yield
        finally:
            api.portal.set_registry_record(FEATURE_FLAGS[feature], before)

    def features(self, *features):
        return nested(*map(self.feature, features))
