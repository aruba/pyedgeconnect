import ApplianceInfo
import DeploymentInfo

class PreconfigFromExisting:
    def __init__(self, ne_pk, upload_to_orch=False):
        self.ne_pk = ne_pk
        self.upload_to_orch = upload_to_orch

    def run(self):
        appliance_info = ApplianceInfo.ApplianceInfo(self.ne_pk, self.upload_to_orch)
        deployment_info = DeploymentInfo.DeploymentInfo(self.ne_pk, self.upload_to_orch)
        # TODO: need to get string from each (preconfig), aggregate as one string, verify it is valid, and then upload if set to true
