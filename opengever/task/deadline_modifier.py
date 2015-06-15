from five import grok
from opengever.base.request import dispatch_request
from opengever.task.activities import TaskTransitionActivity
from opengever.task.browser.transitioncontroller import get_conditions
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from Products.CMFDiffTool.utils import safe_utf8
from zExceptions import Unauthorized
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class DeadlineModifier(grok.Adapter):
    grok.context(ITask)
    grok.implements(IDeadlineModifier)

    def is_modify_allowed(self, include_agency=True):
        """Check if the current user is allowed to modify the deadline:
        - state is `in-progress` or `open`
        - and is issuer or agency member (adminstrator or issuing
        orgunit agency member).
        """
        # TODO: should be solved by a own permission 'modify_deadline'
        # but right now the issuer has not a sperate role.

        if not self.context.is_editable:
            return False

        conditions = get_conditions(self.context)
        if not include_agency:
            return conditions.is_issuer
        else:
            return (conditions.is_issuer or
                    conditions.is_issuing_orgunit_agency_member or
                    conditions.is_administrator)

    def modify_deadline(self, new_deadline, text, transition):
        """Handles the whole deadline mofication process:
        - Set the new deadline
        - Add response
        - Handle synchronisation if needed
        """

        if not self.is_modify_allowed():
            raise Unauthorized

        self.update_deadline(new_deadline, text, transition)
        self.sync_deadline(new_deadline, text, transition)

    def update_deadline(self, new_deadline, text, transition):
        response = add_simple_response(
            self.context, text=text,
            field_changes=(
                (ITask['deadline'], new_deadline),
            ),
            transition=transition
        )

        self.record_activity(response)

        self.context.deadline = new_deadline
        notify(ObjectModifiedEvent(self.context))

    def record_activity(self, response):
        TaskTransitionActivity(self.context, response).record()

    def sync_deadline(self, new_deadline, text, transition):
        sct = ISuccessorTaskController(self.context)
        for successor in sct.get_successors():

            response = dispatch_request(
                successor.admin_unit_id,
                '@@remote_deadline_modifier',
                successor.physical_path,
                data={
                    'new_deadline': new_deadline.toordinal(),
                    'text': safe_utf8(text),
                    'transition': transition})

            if response.read().strip() != 'OK':
                raise Exception(
                    'Updating deadline on remote client %s. failed (%s)' % (
                        successor.admin_unit_id, response.read()))
