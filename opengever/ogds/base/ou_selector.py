from collections import OrderedDict
from Products.CMFPlone import PloneMessageFactory as pmf


CURRENT_ORG_UNIT_KEY = 'current_org_unit_v2'


class OrgUnitSelector(object):

    def __init__(self, storage, admin_unit_units, users_units):
        if not admin_unit_units:
            raise ValueError(
                'The OrgUnitSelector needs at least one possible current unit.'
            )

        self._storage = storage

        self._admin_unit_units = OrderedDict(
            (u.id(), u) for u in admin_unit_units)

        self._users_units = OrderedDict(
            (u.id(), u) for u in users_units)

    def get_current_unit(self):
        unit = self._admin_unit_units.get(self._get_current_unit_id())

        if not unit:
            unit = self._get_fallback_unit()
            self.set_current_unit(unit.id())

        return unit

    def set_current_unit(self, unitid):
        self._storage[CURRENT_ORG_UNIT_KEY] = unitid

    def available_units(self):
        return self._users_units.values()

    def _get_current_unit_id(self):
        if CURRENT_ORG_UNIT_KEY in self._storage:
            return self._storage[CURRENT_ORG_UNIT_KEY]

    def _get_fallback_unit(self):
        # Build intersection of current admin units' org units
        # and user's org units
        user_local_units = [u for u in self._users_units.values()
                            if u in self._admin_unit_units.values()]
        # If some of the user's org units are in the current admin unit,
        # use the first of those as the fallback
        if user_local_units:
            return user_local_units[0]
        # Otherwise we're in an inter-admin unit operation, default to
        # current admin unit's first org unit
        return self._admin_unit_units.values()[0]


class AnonymousOrgUnitSelector(object):

    def __init__(self):
        self._current_unit = NullOrgUnit()

    def get_current_unit(self):
        return self._current_unit

    def set_current_unit(self, unitid):
        raise RuntimeError("Anonymous users can't set current org unit")

    def available_units(self):
        return []


class NoAssignedUnitsOrgUnitSelector(AnonymousOrgUnitSelector):

    def set_current_unit(self, unitid):
        raise RuntimeError(
            "The current user is not assigned to any org units.")


class NullOrgUnit(object):

    def id(self):
        return '__dummy_unit_id__'

    def label(self):
        return pmf('tabs_home', default="Home")

    def public_url(self):
        return '__dummy_public_url__'

    def inbox_group(self):
        return None

    def assigned_users(self):
        return []

    def users_group(self):
        return None

    def inbox(self):
        return NullInbox()

    def prefix_label(self, label):
        return label

    @property
    def admin_unit(self):
        return None

    @property
    def is_inboxgroup_agency_active(self):
        return False


class NullInbox(object):

    def id(self):
        return '__dummy_inbox_id__'

    def assigned_users(self):
        return []
