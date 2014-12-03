from opengever.core.model import create_session
from opengever.globalindex.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.model.proposal import Proposal as ProposalModel
from plone.dexterity.content import Container
from plone.directives import form
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent


class IProposal(form.Schema):
    """Proposal Schema Interface"""


class Proposal(Container):
    """Act as proxy for the proposal stored in the database.

    """
    implements(IProposal)

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return ProposalModel.query.get_by_oguid(oguid)

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        return [
            {
                'label': _('label_title'),
                'value': model.title,
            },
            {
                'label': _('label_initial_position'),
                'value': model.initial_position,
            },

        ]

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
        return '/'.join(url_tool.getRelativeContentPath(self))

    def create_model(self, data, context):
        session = create_session()
        oguid = Oguid.for_object(self)

        aq_wrapped_self = self.__of__(context)
        session.add(ProposalModel(
            oguid=oguid,
            physical_path=aq_wrapped_self.get_physical_path(),
            **data))

        # for event handling to work, the object must be acquisition-wrapped
        notify(ObjectModifiedEvent(aq_wrapped_self))

    def get_searchable_text(self):
        """Return the searchable text for this proposal.

        This method is called during object-creation, thus the model might not
        yet be created (e.g. when the object is added to its parent).

        """
        model = self.load_model()
        if not model:
            return ''

        return model.get_searchable_text()
