from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import FilteredListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


@implementer(ITableSource)
@adapter(IProposalTableSourceConfig, Interface)
class ProposalTableSource(SqlTableSource):

    searchable_columns = []


def proposal_link(item, value):
    return item.get_link()


def translated_state(item, value):
    wrapper = '<span class="wf-proposal-state-{0}">{1}</span>'
    return wrapper.format(
        item.get_state().title,
        translate(item.get_state().title, context=getRequest()))


class ActiveProposalFilter(Filter):
    """Only display active (from the dossiers side) Proposals."""

    def update_query(self, query):
        return query.active()


class DecidedProposalFilter(Filter):
    """Only display decided Proposals."""

    def update_query(self, query):
        return query.decided()


class ProposalListingTab(FilteredListingTab):
    implements(IProposalTableSourceConfig)

    filterlist_name = 'proposal_state_filter'
    filterlist = FilterList(
        Filter(
            'filter_proposals_all',
            _('all', default=u'All')),
        ActiveProposalFilter(
            'filter_proposals_active',
            _('active', default=u'Active'),
            default=True),
        DecidedProposalFilter(
            'filter_proposals_decided',
            _('decided', default=u'Decided'))
        )

    sort_on = ''
    show_selects = False

    @property
    def columns(self):
        return (
            {'column': 'proposal_id',
             'column_title': _(u'label_proposal_id',
                               default=u'Reference Number')},

            {'column': 'decision_number',
             'column_title': _(u'label_decision_number',
                               default=u'Decision number'),
             'transform': lambda item, value: item.get_decision_number()},

            {'column': 'title',
             'column_title': _(u'column_title', default=u'Title'),
             'transform': proposal_link},

            {'column': 'workflow_state',
             'column_title': _(u'column_state', default=u'State'),
             'transform': translated_state},

            {'column': 'committee_id',
             'column_title': _(u'column_comittee', default=u'Comittee'),
             'transform': lambda item, value: item.committee.get_link()},

            {'column': 'generated_meeting_link',
             'column_title': _(u'column_meeting', default=u'Meeting'),
             'transform': lambda item, value: item.get_meeting_link()},

        )

    def get_base_query(self):
        return Proposal.query.by_container(
            self.context, get_current_admin_unit())
