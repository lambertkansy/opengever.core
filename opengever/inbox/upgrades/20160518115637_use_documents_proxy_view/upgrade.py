from ftw.upgrade import UpgradeStep
from plone import api


class UseDocumentsProxyView(UpgradeStep):
    """Use documents proxy view.
    """

    old_action_id = 'documents'
    new_action_id = 'documents-proxy'

    def __call__(self):
        self.install_upgrade_profile()
        self.change_documents_tab_to_documents_proxy_tab()

    def change_documents_tab_to_documents_proxy_tab(self):
        """To choose which template the user has selected before (list or gallery)
        with activated bumblebeefeature, we have to add a proxy view.

        The tabs are stored in actions. So we have to update them to the new
        proxy-view.
        """
        ttool = api.portal.get_tool('portal_types')
        inbox_fti = ttool.get('opengever.inbox.inbox')

        for action in inbox_fti._actions:
            if not action.id == self.old_action_id:
                continue

            action.id = self.new_action_id
