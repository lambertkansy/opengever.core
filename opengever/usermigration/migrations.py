"""
XXX: In a later refactoring, this style of registering migrations should be
cleaned up (no more indirection with "Migrations" that delegate to "Migrators")

For now we leave this as-is though in order to maintain backwards
compatibility and ease backporting.
"""

from opengever.usermigration.creator import CreatorMigrator
from opengever.usermigration.dictstorage import DictstorageMigrator
from opengever.usermigration.dossier import DossierMigrator
from opengever.usermigration.ogds import OGDSMigrator


class OGDSMigration(object):

    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def execute(self, principal_mapping, mode):
        migrator = OGDSMigrator(self.portal, principal_mapping,
                                mode=mode, strict=True)
        results = migrator.migrate()
        return results


class DossierMigration(object):

    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def execute(self, principal_mapping, mode):
        migrator = DossierMigrator(self.portal, principal_mapping,
                                   mode=mode, strict=True)
        results = migrator.migrate()
        return results


class CreatorMigration(object):

    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def execute(self, principal_mapping, mode):
        migrator = CreatorMigrator(self.portal, principal_mapping,
                                   mode=mode, strict=True)
        results = migrator.migrate()
        return results


class DictstorageMigration(object):

    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def execute(self, principal_mapping, mode):
        migrator = DictstorageMigrator(self.portal, principal_mapping,
                                       mode=mode, strict=True)
        results = migrator.migrate()
        return results
