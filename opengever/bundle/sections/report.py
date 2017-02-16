from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from datetime import datetime
from opengever.base.pathfinder import PathFinder
from opengever.bundle.report import ASCIISummaryBuilder
from opengever.bundle.report import DataCollector
from opengever.bundle.report import XLSXReportBuilder
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import json
import logging
import os
import tempfile


log = logging.getLogger('opengever.bundle.report')
log.setLevel(logging.INFO)


class ReportSection(object):
    """Create import reports for the current OGGBundle.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.report_dir = None

    def __iter__(self):
        for item in self.previous:
            yield item

        log.info("Creating import reports...")
        self.report_dir = self.create_report_dir()

        self.store_as_json(self.bundle.errors, 'errors.json')
        self.store_as_json(self.bundle.stats, 'stats.json')

        report_data = DataCollector(self.bundle)()
        self.bundle.report_data = report_data

        self.build_ascii_summary(report_data)
        self.build_xlsx_report(report_data)

    def create_report_dir(self):
        """Create a directory to store all import report files.

        In a real invocation, this will be created inside the instance's
        var/ directory (no git-pollution, variable data where it belongs).

        During tests, a temporary directory will be created.
        """
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dirname = 'import-report-%s' % ts
        try:
            report_dir = os.path.join(PathFinder().var, dirname)
            try:
                os.makedirs(report_dir)
            except OSError:
                # Already exists
                pass
        except RuntimeError:
            # During tests
            report_dir = tempfile.mkdtemp(prefix=dirname)
        return report_dir

    def store_as_json(self, data, filename):
        """Store raw migration stats or errors as JSON files in report dir.
        """
        json_path = os.path.join(self.report_dir, filename)
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, cls=AdvancedJSONEncoder,
                      sort_keys=True, indent=4, separators=(',', ': '))
        log.info('Stored %s' % json_path)

    def build_ascii_summary(self, report_data):
        summary = ASCIISummaryBuilder(report_data).build()
        log.info('\n\n%s\n' % summary)

    def build_xlsx_report(self, report_data):
        report_path = os.path.join(self.report_dir, 'main-report.xlsx')

        xlsx_builder = XLSXReportBuilder(report_data)
        xlsx_builder.build_and_save(report_path)


class AdvancedJSONEncoder(json.JSONEncoder):
    """A custom JSONEncoder that can serialize some additional types:

    - datetime -> ISO-format string
    - set      -> list
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        else:
            # Delegate to the base class
            return json.JSONEncoder.default(self, obj)
