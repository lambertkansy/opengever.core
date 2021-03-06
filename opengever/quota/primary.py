from opengever.quota.interfaces import IObjectSize
from opengever.quota.interfaces import IQuotaSubject
from opengever.trash.trash import ITrashed
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapter
from zope.interface import implementer


class IPrimaryBlobFieldQuota(IQuotaSubject):
    """Behavior for counting the size of the primary field blob
    as usage.
    """


@implementer(IObjectSize)
@adapter(IPrimaryBlobFieldQuota)
class PrimaryFieldQuotaSubject(object):

    def __init__(self, context):
        self.context = context

    def get_size(self):
        """Return the current size of the context in bytes.
        """
        if ITrashed.providedBy(self.context):
            return 0

        primary_field_info = IPrimaryFieldInfo(self.context, None)
        if not primary_field_info or not primary_field_info.value:
            return 0

        return primary_field_info.value.size
