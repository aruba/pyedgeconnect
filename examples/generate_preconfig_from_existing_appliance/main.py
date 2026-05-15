from DeploymentInfo import DeploymentInfo
from ApplianceInfo import ApplianceInfo
from PreconfigFromExisting import PreconfigFromExisting

def main():
    #TODO: create class that aggregates all these classes so only one call needs to be made
    DeploymentInfo("2.NE", upload_to_orch=False)
    # ApplianceInfo("0.NE", upload_to_orch=False)
    # PreconfigFromExisting("6.NE", upload_to_orch=False)

if __name__ == '__main__':
    main()