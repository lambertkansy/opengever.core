"""Contains a view for completeing a task which has a predecesser. Completeing
the successor also completes the predecesser and the user can choose documents
related to the successor task to deliver to issuer by attaching them to the
predecessor task.
"""

from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import encode_after_json
from opengever.ogds.base.utils import remote_request
from opengever.task import _
from opengever.task import util
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import json


@grok.provider(IContextSourceBinder)
def deliverable_documents_vocabulary(context):
    """All documents in the current dossier are deliverable.
    """

    dossier = None
    obj = context
    while not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(obj):
            dossier = obj
        elif dossier and not IDossierMarker.providedBy(obj):
            break

        obj = aq_parent(aq_inner(obj))

    if not dossier:
        raise RuntimeError('Could not find parent dossier.')

    catalog = getToolByName(dossier, 'portal_catalog')
    brains = catalog(portal_type='opengever.document.document',
                     path='/'.join(dossier.getPhysicalPath()))

    # Create the vocabulary.
    terms = []
    intids = getUtility(IIntIds)
    for brain in brains:
        doc = brain.getObject()
        key = str(intids.getId(doc))
        label = '%s (%s, %s)' % (
            doc.Title(),
            IReferenceNumber(doc).get_number(),
            aq_parent(aq_inner(doc)).Title())

        terms.append(SimpleVocabulary.createTerm(key, key, label))

    return SimpleVocabulary(terms)


class ICompleteSuccessorTaskSchema(Schema):

    documents = schema.List(
        title=_(u'label_complete_documents',
                default=u'Documents to deliver'),
        description=_(u'help_complete_documents',
                      default=u'Select the documents you want to deliver to '
                      u'the issuer of the task. They will be attached to the '
                      u'original task of the issuer.'),
        required=False,

        value_type=schema.Choice(
            source=deliverable_documents_vocabulary,
            ))

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_complete_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is completed.'),
        required=False)

    # hidden: used to pass on the transition
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source=util.getTransitionVocab,
        required=True)


class CompleteSuccessorTaskForm(Form):
    fields = Fields(ICompleteSuccessorTaskSchema)
    fields['documents'].widgetFactory = CheckBoxFieldWidget

    label = _(u'title_complete_task', u'Complete task')
    ignoreContext = True

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_save(self, action):
        data, errors = self.extractData()

        if not errors:
            util.change_task_workflow_state(self.context,
                                            data['transition'],
                                            text=data['text'])

            self.deliver_documents_and_complete_task(data)

            msg = _(u'The documents were delivered to the issuer and the '
                    u'tasks were completed.')
            IStatusMessage(self.request).addStatusMessage(msg, 'info')

            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        if self.request.form.get('form.widgets.transition', None) is None:
            self.request.set('form.widgets.transition',
                             self.request.get('transition'))

        # Use text passed from response-add-form.
        if self.request.form.get('form.widgets.text', None) is None:
            dm = getUtility(IWizardDataStorage)
            oguid = ISuccessorTaskController(self.context).get_oguid()
            dmkey = 'delegate:%s' % oguid
            text = dm.get(dmkey, 'text')
            if text:
                self.request.set('form.widgets.text', text)

        Form.updateWidgets(self)

        self.widgets['transition'].mode = HIDDEN_MODE

    def deliver_documents_and_complete_task(self, formdata):
        """Delivers the selected documents to the predecesser task and
        complete the task:

        - Copy the documents to the predecessor task (no new responses)
        - Execute workflow transition (no new response)
        - Add a new response indicating the workflow transition, the added
        documents and containing the entered response text.
        """

        predecessor = getUtility(ITaskQuery).get_task_by_oguid(
            self.context.predecessor)

        transporter = getUtility(ITransporter)
        intids = getUtility(IIntIds)

        data = {'documents': [],
                'text': formdata['text'],
                'transition': formdata['transition']}

        for doc_intid in formdata['documents']:
            doc = intids.getObject(int(doc_intid))
            data['documents'].append(transporter._extract_data(doc))

        request_data = {'data': json.dumps(data)}
        response = remote_request(
            predecessor.client_id,
            '@@complete_successor_task-receive_delivery',
            predecessor.physical_path,
            data=request_data)

        if response.read().strip() != 'OK':
            raise Exception('Delivering documents and updating task failed '
                            'on remote client %s.' % predecessor.client_id)


class CompleteSuccessorTask(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('complete_successor_task')
    grok.require('cmf.AddPortalContent')

    form = CompleteSuccessorTaskForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


class CompleteSuccessorTaskReceiveDelivery(grok.View):
    """This view is called by the complete-sucessor-task form while
    completeing the task. It is called on the client of the predecessor and
    makes the necessary changes regarding the predecessor task:

    - Copy the documents to the predecessor task (no new responses)
    - Execute workflow transition (no new response)
    - Add a new response indicating the workflow transition, the added
    documents and containing the entered response text.
    """

    grok.context(ITask)
    grok.name('complete_successor_task-receive_delivery')
    grok.require('cmf.AddPortalContent')

    def render(self):
        data = self.request.get('data', None)
        assert data is not None, 'Bad request: no delivery data found'
        data = json.loads(data)

        # Set the "X-CREATING-SUCCESSOR" flag for preventing the event
        # handler from creating additional responses per added document.
        self.request.set('X-CREATING-SUCCESSOR', True)

        # Create the delivered documents:
        transporter = getUtility(ITransporter)
        documents = []

        for item in encode_after_json(data['documents']):
            doc = transporter._create_object(self.context, item)
            documents.append(doc)

        # Change workflow state of predecessor task:
        util.change_task_workflow_state(
            self.context, data['transition'], text=data['text'],
            added_object=documents)

        return 'OK'
