from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.document.behaviors.metadata import IDocumentMetadata
from plone.namedfile.file import NamedBlobFile
import os


ARCHIVAL_FILE_STATE_CONVERTING = 1
ARCHIVAL_FILE_STATE_CONVERTED = 2
ARCHIVAL_FILE_STATE_MANUALLY = 3
ARCHIVAL_FILE_STATE_FAILED_TEMPORARILY = 4
ARCHIVAL_FILE_STATE_FAILED_PERMANENTLY = 5


class ArchivalFileConverter(object):

    def __init__(self, document):
        self.document = document

    def trigger_conversion(self):
        if self.get_state() == ARCHIVAL_FILE_STATE_MANUALLY:
            return

        self.set_state(ARCHIVAL_FILE_STATE_CONVERTING)
        IBumblebeeServiceV3(self.document).queue_conversion(
            PROCESSING_QUEUE, self.get_callback_url(), target_format='pdf/a')

    def get_state(self):
        return IDocumentMetadata(self.document).archival_file_state

    def set_state(self, state):
        IDocumentMetadata(self.document).archival_file_state = state

    def get_callback_url(self):
        return "{}/archival_file_conversion_callback".format(
            self.document.absolute_url())

    def store_file(self, data, mimetype='application/pdf'):
        IDocumentMetadata(self.document).archival_file = NamedBlobFile(
            data=data,
            contentType=mimetype,
            filename=self.get_file_name())
        self.set_state(ARCHIVAL_FILE_STATE_CONVERTED)

    def handle_temporary_conversion_failure(self):
        self.set_state(ARCHIVAL_FILE_STATE_FAILED_TEMPORARILY)

    def handle_permanent_conversion_failure(self):
        self.set_state(ARCHIVAL_FILE_STATE_FAILED_PERMANENTLY)

    def set_manually_state(self):
        self.set_state(ARCHIVAL_FILE_STATE_MANUALLY)

    def get_file_name(self):
        filename, ext = os.path.splitext(self.document.file.filename)
        return u'{}.pdf'.format(filename)
