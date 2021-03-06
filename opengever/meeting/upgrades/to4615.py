from ftw.upgrade import UpgradeStep


class UpdateCommitteeContainerWorkflow(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.meeting.upgrades:4615')

        self.update_workflow_security(
            ['opengever_committeecontainer_workflow'],
            reindex_security=False)
