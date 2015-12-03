from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class AgendaItem(Base):
    """An item must either have a reference to a proposal or a title.

    """

    __tablename__ = 'agendaitems'

    # workflow definition
    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_DECIDED = State('decided', title=_('decided', default='Decided'))

    workflow = Workflow(
        [STATE_PENDING, STATE_DECIDED],
        [Transition('pending', 'decided',
                    title=_('decide', default='Decide'))]
    )

    agenda_item_id = Column("id", Integer, Sequence("agendaitems_id_seq"),
                            primary_key=True)
    workflow_state = Column(String(WORKFLOW_STATE_LENGTH), nullable=False,
                            default=workflow.default_state.name)
    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    proposal = relationship("Proposal", uselist=False,
                            backref=backref('agenda_item', uselist=False))
    decision_number = Column(Integer)

    title = Column(UnicodeCoercingText)
    number = Column('item_number', String(16))
    is_paragraph = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)

    discussion = Column(UnicodeCoercingText)
    decision = Column(UnicodeCoercingText)

    def update(self, request):
        """Update with changed data."""

        data = request.get(self.name)
        if not data:
            return

        if self.has_proposal:
            self.proposal.legal_basis = data.get('legal_basis')
            self.proposal.initial_position = data.get('initial_position')
            self.proposal.considerations = data.get('considerations')
            self.proposal.proposed_action = data.get('proposed_action')
            self.proposal.publish_in = data.get('publish_in')
            self.proposal.disclose_to = data.get('disclose_to')
            self.proposal.copy_for_attention = data.get('copy_for_attention')

        self.discussion = data.get('discussion')
        self.decision = data.get('decision')

    def get_field_data(self, include_initial_position=True,
                       include_legal_basis=True, include_considerations=True,
                       include_proposed_action=True, include_discussion=True,
                       include_decision=True, include_publish_in=True,
                       include_disclose_to=True,
                       include_copy_for_attention=True):
        data = {
            'number': self.number,
            'description': self.description,
            'title': self.get_title(),
            'dossier_reference_number': self.get_dossier_reference_number(),
            'is_paragraph': self.is_paragraph,
            'decision_number': self.decision_number,
        }
        if include_initial_position:
            data['markdown:initial_position'] = self._sanitize_text(
                self.initial_position)
        if include_legal_basis:
            data['markdown:legal_basis'] = self._sanitize_text(
                self.legal_basis)
        if include_considerations:
            data['markdown:considerations'] = self._sanitize_text(
                self.considerations)
        if include_proposed_action:
            data['markdown:proposed_action'] = self._sanitize_text(
                self.proposed_action)
        if include_discussion:
            data['markdown:discussion'] = self._sanitize_text(self.discussion)
        if include_decision:
            data['markdown:decision'] = self._sanitize_text(self.decision)
        if include_publish_in:
            data['markdown:publish_in'] = self._sanitize_text(self.publish_in)
        if include_disclose_to:
            data['markdown:disclose_to'] = self._sanitize_text(
                self.disclose_to)
        if include_copy_for_attention:
            data['markdown:copy_for_attention'] = self._sanitize_text(
                self.copy_for_attention)

        return data

    def _sanitize_text(self, text):
        if not text:
            return None

        return text

    def get_title(self, include_number=False):
        title = self.proposal.title if self.has_proposal else self.title
        if include_number and self.number:
            title = u"{} {}".format(self.number, title)

        return title

    def set_title(self, title):
        if self.has_proposal:
            self.proposal.title = title
        else:
            self.title = title

    def get_dossier_reference_number(self):
        if self.has_proposal:
            return self.proposal.dossier_reference_number
        return None

    def get_css_class(self):
        css_classes = []
        if self.is_paragraph:
            css_classes.append("paragraph")
        if self.has_submitted_documents():
            css_classes.append("expandable")
        return " ".join(css_classes)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def remove(self):
        assert self.meeting.is_editable()

        session = create_session()
        if self.proposal:
            self.proposal.remove_scheduled(self.meeting)
        session.delete(self)
        self.meeting.reorder_agenda_items()

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal:
            return self.get_title()

        return self.proposal.get_submitted_link(include_icon=include_icon)

    def serialize(self):
        return {
            'id': self.agenda_item_id,
            'css_class': self.get_css_class(),
            'title': self.get_title(),
            'number': self.number,
            'has_proposal': self.has_proposal,
            'link': self.get_proposal_link(include_icon=False),
            }

    @property
    def has_proposal(self):
        return self.proposal is not None

    @property
    def legal_basis(self):
        return self.proposal.legal_basis if self.has_proposal else None

    @property
    def initial_position(self):
        return self.proposal.initial_position if self.has_proposal else None

    @property
    def considerations(self):
        return self.proposal.considerations if self.has_proposal else None

    @property
    def proposed_action(self):
        return self.proposal.proposed_action if self.has_proposal else None

    @property
    def publish_in(self):
        return self.proposal.publish_in if self.has_proposal else None

    @property
    def disclose_to(self):
        return self.proposal.disclose_to if self.has_proposal else None

    @property
    def copy_for_attention(self):
        return self.proposal.copy_for_attention if self.has_proposal else None

    @property
    def name(self):
        """Currently used as name for input tags in html."""

        return "agenda_item-{}".format(self.agenda_item_id)

    @property
    def description(self):
        return self.get_title()

    def has_submitted_documents(self):
        return self.has_proposal and self.proposal.has_submitted_documents()

    def has_submitted_excerpt_document(self):
        return self.has_proposal and self.proposal.has_submitted_excerpt_document()

    def is_decide_possible(self):
        return self.get_state() == self.STATE_PENDING

    def decide(self):
        if self.has_proposal:
            self.proposal.generate_excerpt(self)
            self.proposal.decide()

        self.meeting.hold()

        self.workflow.execute_transition(None, self, 'pending-decided')
