import os
import sys
from pyedgeconnect import Orchestrator
from utils import generate_preconfig_yaml, _write_local_yaml_file, validate_preconfig
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class ApplianceInfo:
    def __init__(self, ne_pk, upload_to_orch=False):
        self.ne_pk = ne_pk
        self.upload_to_orch = upload_to_orch
        # initialize appliance_info dictionary
        self.appliance_info_details = {
            "softwareVersion": None,
            "hostname": None,
            "group": None,
            "site": None,
            "clusterProfile": None,
            "networkRole": None,
            "region": None,
            "location_address": None,
            "location_address2": None,
            "location_city": None,
            "location_state": None,
            "location_zipCode": None,
            "location_country": None,
            "location_latitude": None,
            "location_longitude": None,
            "contact_name": None,
            "contact_email": None,
            "contact_phoneNumber": None
        }

        # Get env variables. If they do not exist, exit program.
        try:
            orch_url = os.getenv('ORCH_URL')
            orch_api_key = os.getenv('ORCH_API_KEY')

            if not all([orch_url, orch_api_key]):
                raise ValueError(
                    "One or more required environment variables are not set.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        ec_template_file = 'ec_applianceInfo_preconfig_template.jinja2'

        try:
            self.orch = Orchestrator(orch_url, api_key=orch_api_key, verify_ssl=False)
            self.appliance_extra_info = self.orch.get_appliance_extra_info(ne_pk=ne_pk)
            self.appliance = self.orch.get_appliances(ne_pk=ne_pk)
        except Exception as e:
            print(f"Failed to connect to Orchestrator or fetch appliance data: {str(e)}")

        # Get data and put in appliance_info dictionary
        self.appliance_info_details['softwareVersion'] = self._get_active_appliance_version(self.orch)
        self.appliance_info_details['contact_name'] = self.appliance_extra_info['contact']['name']
        self.appliance_info_details['contact_email'] = self.appliance_extra_info['contact']['email']
        self.appliance_info_details['contact_phoneNumber'] = self.appliance_extra_info['contact']['phoneNumber']
        self.appliance_info_details['location_address'] = self.appliance_extra_info['location']['address']
        self.appliance_info_details['location_address2'] = self.appliance_extra_info['location']['address2']
        self.appliance_info_details['location_city'] = self.appliance_extra_info['location']['city']
        self.appliance_info_details['location_state'] = self.appliance_extra_info['location']['state']
        self.appliance_info_details['location_zipCode'] = self.appliance_extra_info['location']['zipCode']
        self.appliance_info_details['location_country'] = self.appliance_extra_info['location']['country']
        self.appliance_info_details['hostname'] = self.appliance['hostName']
        self.appliance_info_details['site'] = self.appliance['site']
        self.appliance_info_details['group'] = self._get_appliance_group(self.appliance['groupId'])
        self.appliance_info_details['networkRole'] = self._get_appliance_network_role(self.orch)
        self.appliance_info_details['region'] = self.orch.get_region_appliance_association_by_nepk(ne_pk=self.ne_pk)['regionName']


        # TODO: Need to check orch version as to whether or not to include clusterProfile
        if self._should_include_cluster_profile():
            self.appliance_info_details['clusterProfile'] = self._get_cluster_profile_name_by_cluster_profile_uuid_mapping()
            self.appliance_info_details['should_include_cluster_profile'] = True
        else:
            self.appliance_info_details['should_include_cluster_profile'] = False

        pprint(self.appliance_info_details)
        print('-----------------------------------------------')
        yaml_preconfig = self._generate_preconfig_yaml()
        print(yaml_preconfig)
        if validate_preconfig(self.orch, yaml_preconfig):
            print('Preconfig for ApplianceInfo is valid')
            if upload_to_orch:
                preconfig_name = f"{self.appliance_info_details['hostname']}_applianceInfo-AUTOMATED_PRECONFIG"

                try:
                    self.orch.create_preconfig(preconfig_name=preconfig_name,
                                          yaml_preconfig=yaml_preconfig,
                                          auto_apply=False,
                                          serial_number=self.appliance['serial'].replace("-", ""),
                                          comment="Created via automation"
                                          )
                    print(f"Preconfig '{preconfig_name}' created SUCCESSFULLY on Orchestrator")
                except Exception as e:
                    print(f"ERROR creating preconfig '{preconfig_name}' on Orchestrator")
        else:
            print('Preconfig for ApplianceInfo is NOT valid')


    def _generate_preconfig_yaml(self):
        ec_template_file = 'ec_applianceInfo_preconfig_template.jinja2'
        device_name = self.appliance_info_details['hostname']
        preconfig_section_name = "applianceInfo"
        preconfig_yaml = generate_preconfig_yaml(self.appliance_info_details, preconfig_section_name, ec_template_file, device_name)
        return preconfig_yaml
        # write_local_yaml_file(preconfig_yaml)
        # validate_preconfig(preconfig_yaml)


    def _get_cluster_profile_uuid_to_device_mapping(self):
        cluster_profile_mappings = self.orch.get_all_cluster_profile_mappings()
        for uuid, values in cluster_profile_mappings.items():
            if self.appliance_info_details['site'] in values:
                return uuid
            else:
                return None

    def _get_cluster_profile_name_by_cluster_profile_uuid_mapping(self):
        cluster_profile_uuid = self._get_cluster_profile_uuid_to_device_mapping()
        cluster_profiles = self.orch.get_all_cluster_profiles()
        for profile in cluster_profiles:
            if profile['id'] == cluster_profile_uuid:
                return profile['name']
        return ''


    def _should_include_cluster_profile(self) -> bool:
        if self.orch.orch_version < 9.5:
            return False
        else:
            return True

    def _get_active_appliance_version(self, orch) -> str:
        data = orch.get_appliance_software_version(ne_pk=self.ne_pk, cached=False)
        for entry in data:
            if entry['active']:
                return entry['build_version']
        return ''


    def _get_appliance_group(self, appliance_group_id) -> str:
        data = self.orch.get_gms_groups()
        for group in data:
            if group['id'] == appliance_group_id:
                return group['name']
        return ''

    def _get_appliance_network_role(self, orch) -> str:
        data = orch.get_appliance_network_role_and_site(ne_id=self.ne_pk)
        network_role = data['networkRole']
        # These were the only options I saw in the various return values. What happened to 2?
        if network_role == '0':
            return 'non-hub'
        elif network_role == '1':
            return 'hub'
        elif network_role == '3':
            return 'nrhub'
        else:
            return ''




