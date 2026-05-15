from __future__ import annotations
import sys
import os

from dotenv import load_dotenv
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
from pyedgeconnect import Orchestrator

load_dotenv()

class DeploymentInfo:
    def __init__(self, ne_pk, upload_to_orch=False):
        self.ne_pk = ne_pk
        self.upload_to_orch = upload_to_orch

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

        ec_template_file = 'ec_deployment_preconfig_template.jinja2'

        orch = Orchestrator(orch_url, api_key=orch_api_key, verify_ssl=False)

        # Orchestrator version information
        orch_version = orch.get_orchestrator_server_versions()
        orch_major_version = orch_version['current'].split('.')[0]
        orch_minor_version = orch_version['current'].split('.')[1]

        # Check to ensure Orchestrator is Version 9.3 or higher. If not, exit program.
        if (int(orch_major_version) < 9) or (int(orch_major_version) == 9 and int(orch_minor_version) <= 2):
            print("This script currently only supports Orchestrator version 9.3 and higher. Exiting.")
            sys.exit(0)

        # Get initial data from API endpoints
        appliance_info = orch.get_appliances(ne_pk=ne_pk)
        device_name = appliance_info['hostName']
        deployment_info = orch.get_appliance_deployment(ne_pk=ne_pk)
        extra_info = orch.get_appliance_extra_info(ne_pk=ne_pk)
        appliance_tunnel_info = orch.appliance_get_api(ne_pk=ne_pk, url="tunnels/pass-through")

        # Appliance version information (patch version not currently used - future use)
        appliance_software_version = appliance_info['softwareVersion']
        appliance_major_version = appliance_software_version.split('.')[0]
        appliance_minor_version = appliance_software_version.split('.')[1]
        appliance_patch_version = appliance_software_version.split('.')[2]

        # Gather EdgeHA info if it exists
        ha_peer = orch.get_ha_peer_meta(ne_pk=ne_pk)
        # is_edge_ha = False
        ha_config = {}
        try:
            # if there is no 'nePK' key, the device has no EdgeHA peer
            peer_ne_pk = ha_peer[ne_pk]['nePk']
            is_edge_ha = True
        except KeyError:
            print('No peer')
            is_edge_ha = False
            peer_ne_pk = None

        if is_edge_ha:
            ha_config = self._get_edge_ha_info(
                deployment_info,
                ha_config,
                ne_pk,
                orch,
                peer_ne_pk
            )

        # Get DHCP support capabilities (based on SW versions)
        (is_option82_suboption_supported,
         is_option_82_suboption_required,
         server_per_segment_preconfig_yaml_support) = self._dhcp_options_check(
            appliance_major_version,
            appliance_minor_version,
            orch_major_version,
            orch_minor_version)

        dhcp_info_list = self._get_dhcp_info(
            deployment_info,
            is_option82_suboption_supported,
            is_option_82_suboption_required
        )

        is_dhcp_configured = True if len(dhcp_info_list) > 0 else False

        # if not using API key, logout from Orchestrator
        if orch_api_key is None:
            orch.logout()
        else:
            pass

        # Get back rendered preconfig as string
        preconfig_yaml = self._generate_preconfig_yaml(
            appliance_tunnel_info,
            deployment_info,
            device_name,
            dhcp_info_list,
            ec_template_file,
            extra_info,
            ha_config,
            is_dhcp_configured,
            server_per_segment_preconfig_yaml_support
        )

        preconfig_name = f"{device_name}_deploymentInfo-AUTOMATED_PRECONFIG"

        is_preconfig_valid = self._validate_preconfig(orch, preconfig_yaml)
        if is_preconfig_valid and self.upload_to_orch is True:
            orch.create_preconfig(preconfig_name=preconfig_name,
                                  yaml_preconfig=preconfig_yaml,
                                  auto_apply=False,
                                  serial_number=appliance_info['serial'].replace("-", ""),
                                  comment="Created via automation"
            )


    # TODO: change this to use the utils.py function instead
    def _validate_preconfig(self, orch, preconfig_yaml) -> bool:

        """

        The `validate_preconfig` function checks if a given YAML preconfiguration (`preconfig_yaml`) is valid by using the
        (`orch`) object's`validate_preconfig` method.

        It returns `True` if the validation is successful (HTTP status code 200) and prints "Preconfig is valid." Otherwise,
        it returns `False` and prints an error message.

        """

        validity_check = orch.validate_preconfig(preconfig_name="temp", yaml_preconfig=preconfig_yaml, auto_apply=False)
        if validity_check.status_code == 200:
            print("Preconfig is valid.")
            return True
        else:
            print("Preconfig is NOT valid. Please look at error response for details.")


    # TODO: change this to use the utils.py function instead
    def _generate_preconfig_yaml(self, appliance_tunnel_info, deployment_info, device_name, dhcp_info_list, ec_template_file,
                                 extra_info, ha_config, is_dhcp_configured, server_per_segment_preconfig_yaml_support) -> str:
        """

            The `generate_preconfig_yaml` function creates a YAML configuration file for an EdgeConnect device.

            It uses a Jinja2 template (`ec_template_file`) along with various inputs like device details, deployment info,
            tunnel settings, DHCP configuration, and high availability settings to generate the YAML content.

            The function ensures the output is saved to the `preconfig_outputs/` directory and returns the generated YAML
            file's content as a string.

        """

        env = Environment(
            loader=FileSystemLoader("templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        ec_template = env.get_template(ec_template_file)
        # Local directory for configuration outputs
        output_directory = "preconfig_outputs/"

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        yaml_preconfig = self._write_local_yaml_file(appliance_tunnel_info, deployment_info, device_name, dhcp_info_list,
                                                     ec_template, extra_info, ha_config, is_dhcp_configured, output_directory,
                                                     server_per_segment_preconfig_yaml_support)

        return yaml_preconfig


    # TODO: change this to use the utils.py function instead
    def _write_local_yaml_file(self, appliance_tunnel_info, deployment_info, device_name, dhcp_info_list, ec_template, extra_info,
                               ha_config, is_dhcp_configured, output_directory, server_per_segment_preconfig_yaml_support):

        """

        The `write_local_yaml_file` function generates a YAML file for an EdgeConnect device using a Jinja2 template
        (`ec_template`) and the provided configuration details.

        The generated YAML is saved in the specified `output_directory` with a filename based on the device name, and the
        YAML content is also returned as a string.

        """

        yaml_filename = f"{device_name}_AUTOMATED_PRECONFIG.yml"
        yaml_preconfig = ec_template.render(
            device_name=device_name,
            deployment_info=deployment_info,
            extra_info=extra_info,
            appliance_tunnel_info=appliance_tunnel_info,
            ha_config=ha_config,
            is_dhcp_configured=is_dhcp_configured,
            dhcp_info=dhcp_info_list,
            server_per_segment_preconfig_yaml_support=server_per_segment_preconfig_yaml_support,
        )
        with open(output_directory + yaml_filename, "w") as preconfig_file:
            write_data = preconfig_file.write(yaml_preconfig)
        return yaml_preconfig


    def _dhcp_options_check(self, appliance_major_version, appliance_minor_version, orch_major_version, orch_minor_version):

        """
        The `dhcp_options_check` function determines the support and requirements for specific DHCP features based on the
        major and minor versions of the appliance and orchestrator.

        It returns three boolean values:
        1. Whether option 82 suboptions are supported.
        2. Whether option 82 suboptions are required.
        3. Whether the 'serverPerSegment' option is supported in the preconfiguration YAML.

        """

        # Check if option82 suboptions are supported - only 9.5.1 on Orch and ECOS support it
        # No need to put in for loop - it only needs to be determined once
        if int(appliance_major_version) >= 9 and int(appliance_minor_version) >= 5 and \
                int(orch_major_version) >= 9 and int(orch_minor_version) >= 5:
            is_option82_suboption_supported = True
        else:
            is_option82_suboption_supported = False
        # In Orch 9.5, specifying suboptions for option 82 is required - even for appliances
        # running 9.4 and lower. This will be tested and a note added to Jinja template
        if int(appliance_major_version) >= 9 and int(appliance_minor_version) <= 4 and \
                int(orch_major_version) >= 9 and int(orch_minor_version) >= 5:
            is_option_82_suboption_required_but_not_supported_on_ecos = True
        else:
            is_option_82_suboption_required_but_not_supported_on_ecos = False
        # Check if the 'serverPerSegment' option is supported in the preconfig YAML - 9.5 and higher
        if int(orch_major_version) >= 9 and int(orch_minor_version) >= 5:
            server_per_segment_preconfig_yaml_support = True
        else:
            server_per_segment_preconfig_yaml_support = False
        return is_option82_suboption_supported, is_option_82_suboption_required_but_not_supported_on_ecos, server_per_segment_preconfig_yaml_support


    def _get_dhcp_info(self, deployment_info, is_option82_suboption_supported, is_option_82_suboption_required_but_not_supported_on_ecos):

        """
        The `get_dhcp_info` function extracts and organizes DHCP configuration details from the `deployment_info` input.

        It processes interfaces marked for DHCP server or relay, gathers necessary settings (like IP ranges, DNS servers,
        gateway, lease times, failover details, and option 82 configurations), and returns a list of DHCP configuration
        dictionaries (`dhcp_info_list`) that can be used for further processing, such as generating a YAML file.

        """

        is_dhcp_configured = False
        dhcp_ha_interface_list = []
        dhcp_info_list = []
        for info in deployment_info['modeIfs']:
            for appliance_ip_data in info['applianceIPs']:
                if self._is_field_present(appliance_ip_data, 'dhcpd'):
                    # Gather DHCP server info-------------------------------------------
                    # Initialize variables - otherwise variables carryover between loop iterations below
                    # if multiple interfaces are using a combination of DHCP Server and Relay - different
                    # data for each but I'm using the same dictionary: dhcp_info_dict
                    dhcp_interface_name = ''
                    dhcp_type = ''
                    dhcp_address_mask = ''
                    start_ip_address = ''
                    end_ip_address = ''
                    ip_ranges = []
                    gateway_ip_address = ''
                    dns_servers = []
                    ntp_servers = []
                    netbios_name_servers = []
                    netbios_node_type = ''
                    maximum_lease = ''
                    default_lease = ''
                    dhcp_options = []
                    static_host_entries = []
                    failover = False
                    dhcp_failover_role = ''
                    dhcp_failover_my_ip = ''
                    dhcp_failover_my_port = ''
                    dhcp_failover_peer_ip = ''
                    dhcp_failover_peer_port = ''
                    dhcp_failover_max_resp_delay = ''
                    dhcp_failover_max_unack_updates = ''
                    dhcp_failover_load_bal_max = ''
                    dhcp_failover_mclt = ''
                    dhcp_failover_split = ''
                    dhcp_proxy_servers = []
                    enable_options_82 = False
                    options_82_policy = ''
                    option82_suboptions = []

                    # dhcp_configured = True
                    if 'vlan' in appliance_ip_data:
                        dhcp_interface_name = f"{info['ifName']}.{appliance_ip_data['vlan']}"
                    else:
                        dhcp_interface_name = info['ifName']

                    # Interface must be lan side
                    if appliance_ip_data['lanSide']:
                        # Gather data and put in dict
                        dhcp_data_for_interface = appliance_ip_data['dhcpd']
                        if dhcp_data_for_interface['type'] == 'relay':
                            is_dhcp_configured = True
                            # Interface is set for DHCP Relay
                            # Get all DHCP Relay data
                            dhcp_type = 'relay'

                            for dhcp_server in dhcp_data_for_interface['relay']['dhcpserver']:
                                dhcp_proxy_servers.append(dhcp_server)

                            enable_options_82 = dhcp_data_for_interface['relay']['option82']
                            options_82_policy = dhcp_data_for_interface['relay']['option82_policy']

                            # Get option 82 suboptions if supported by ECOS and Orchestrator)
                            if is_option82_suboption_supported:
                                for key, value in dhcp_data_for_interface['relay'].items():
                                    if 'opt82SubOpt' in key:
                                        option82_suboptions.append({'option': key, 'value': value})

                        if dhcp_data_for_interface['type'] == 'server':
                            is_dhcp_configured = True
                            # Interface is set for DHCP Server
                            # Get all DHCP server data
                            dhcp_type = 'server'
                            dhcp_address_mask = dhcp_data_for_interface['server']['prefix']
                            start_ip_address = dhcp_data_for_interface['server']['ipStart']
                            end_ip_address = dhcp_data_for_interface['server']['ipEnd']

                            ip_ranges = []
                            for key, value in dhcp_data_for_interface['server']['ip_range'].items():
                                ip_ranges.append({'start_ip': value['start'], 'end_ip': value['end']})

                            #TODO: need to check for blank GW address
                            gateway_ip_address = dhcp_data_for_interface['server']['gw'][0]

                            dns_servers = []
                            for dns_server in dhcp_data_for_interface['server']['dns']:
                                dns_servers.append(dns_server)

                            ntp_servers = []
                            for ntp_server in dhcp_data_for_interface['server']['ntpd']:
                                ntp_servers.append(ntp_server)

                            netbios_name_servers = []
                            for netbios_name_server in dhcp_data_for_interface['server']['netbios']:
                                netbios_name_servers.append(netbios_name_server)

                            netbios_node_type = dhcp_data_for_interface['server']['netbiosNodeType']
                            maximum_lease = dhcp_data_for_interface['server']['maxLease']
                            default_lease = dhcp_data_for_interface['server']['defaultLease']

                            dhcp_options = []
                            for key, value in dhcp_data_for_interface['server']['options'].items():
                                dhcp_options.append({'option': key, 'value': value})

                            static_host_entries = []
                            # Get static host entries if they exist
                            if len(dhcp_data_for_interface['server']['host']) > 0:
                                for key, value in dhcp_data_for_interface['server']['host'].items():
                                    static_host_entries.append(
                                        {'hostname': key, 'mac_address': value['mac'], 'ip_address': value['ip']})

                            # DCHP HA Failover
                            if dhcp_data_for_interface['server']['failover'] == True:
                                failover = True
                                # There is only one DHCP HA Failover configuration per physical interface.
                                # However, in the Preconfig YAML, in order to enable DHCP Failover for a sub-interface,
                                # the 'dhcpHA' section for each sub-intervace must be configured in its entirety - each
                                # having the exact same dhcpHA configuration.

                                dhcp_failover_main_interface = info['ifName']

                                # if dhcpHA is not already configured for main interface in this main loop
                                # configure it. Reminder: only one dhcpHA config per main interface - not sub-interfaces
                                # if dhcp_failover_main_interface not in dhcp_ha_interface_list:
                                dhcp_failover_role = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['role']
                                dhcp_failover_my_ip = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['my_ip']
                                dhcp_failover_my_port = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['my_port']
                                dhcp_failover_peer_ip = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['peer_ip']
                                dhcp_failover_peer_port = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['peer_port']
                                dhcp_failover_max_resp_delay = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['max_resp_delay']
                                dhcp_failover_max_unack_updates = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['max_unack_updates']
                                dhcp_failover_load_bal_max = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['load_bal_max']
                                dhcp_failover_mclt = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['mclt']
                                dhcp_failover_split = deployment_info['dhcpFailover'][dhcp_failover_main_interface]['split']

                                # Add configured dhcpHA main interface to list to be checked upon next major loop iteration.
                                # Reminder: only one dhcpHA config per main interface - not per sub-interface
                                # dhcp_ha_interface_list.append(dhcp_failover_main_interface)

                            else:
                                failover = False

                        # Create custom dict to add to 'dhcp_info_list' that can be iterated over in Jinja template
                        dhcp_info_dict = {
                            'dhcpInterfaceName': dhcp_interface_name,
                            'dhcpType': dhcp_type,
                            'dhcpAddressMask': dhcp_address_mask,
                            'startIpAddress': start_ip_address,
                            'endIpAddress': end_ip_address,
                            'ipRanges': ip_ranges  # list[dict]
                            # {'start_ip': '198.168.0.101', 'end_ip': '198.168.0.110'},
                            # {'start_ip': '198.168.0.111', 'end_ip': '198.168.0.120'}
                            ,
                            'gatewayIpAddress': gateway_ip_address,
                            'dnsServers': dns_servers,
                            'ntpServers': ntp_servers,
                            'netbiosNameServers': netbios_name_servers,
                            'netbiosNodeType': netbios_node_type,
                            'maximumLease': maximum_lease,
                            'defaultLease': default_lease,
                            'options': dhcp_options  # list[dict]
                            # {'option': 1, 'value': '255.255.255.0'}
                            ,
                            'staticIpAssignments': static_host_entries  # list[dict]
                            # {
                            #     'hostname': 'google',
                            #     'macAddress': '00:25:96:FF:FE:12',
                            #     'ipAddress': '198.168.0.7'
                            # }
                            ,
                            'failover': failover,
                            'dhcpFailoverRole': dhcp_failover_role,
                            'dhcpFailoverMyIp': dhcp_failover_my_ip,
                            'dhcpFailoverMyPort': dhcp_failover_my_port,
                            'dhcpFailoverPeerIp': dhcp_failover_peer_ip,
                            'dhcpFailoverPeerPort': dhcp_failover_peer_port,
                            'dhcpFailoverMCLT': dhcp_failover_mclt,
                            'dhcpFailoverSplit': dhcp_failover_split,
                            'dhcpFailoverMaxRespDelay': dhcp_failover_max_resp_delay,
                            'dhcpFailoverMaxUnackUpdates': dhcp_failover_max_unack_updates,
                            'dhcpFailoverLoadBalMax': dhcp_failover_load_bal_max,

                            'dhcpProxyServers': dhcp_proxy_servers,
                            'enableOptions82': enable_options_82,
                            'options82Policy': options_82_policy,
                            'option82SuboptionSupport': is_option82_suboption_supported,
                            'option82SubOptions': option82_suboptions,
                            'option82SubOptionsRequiredButNotSupportedOnECOS': is_option_82_suboption_required_but_not_supported_on_ecos,

                            # TODO: Note-> under main deploymentInfo section is "serverPerSegment". It is a new option for new code that needs to be checked against software versions. Its for DHCP Relay settings, but is up higher in the YAML config file.

                            # TODO: Add dhcpHA subsection when the API endpoint is available
                        }
                        # Add dhcp info to list. The list will be iterated over in the Jinja template for each interface
                        dhcp_info_list.append(dhcp_info_dict)
        return dhcp_info_list


    def _get_edge_ha_info(self, deployment_info, ha_config, ne_pk, orch, peer_ne_pk):
        """
        The `get_edge_ha_info` function retrieves and organizes High Availability (HA) configuration information for an
        EdgeConnect device and its peer device.

        It performs the following:
        1. Retrieves data such as peer hostname, HA IP pool, subnet mask, VLAN start values, and HA interface details.
        2. Maps HA interface labels and orders them based on their configurations for both the local and peer device.
        3. Gathers additional traffic shaper details (e.g. outbound, inbound shapers), segments, and zone information.
        4. Compiles all this HA configuration information into a dictionary (`ha_config`) which can be used for further
           processing, such as generating a configuration using a template.

        The function returns the `ha_config` dictionary.
        """
        appliance_info = orch.get_appliances(ne_pk=peer_ne_pk)
        peer_hostname = None
        try:
            peer_hostname = appliance_info['hostName']
        except KeyError:
            print('KeyError!!!')
        ha_groups = orch.get_ha_groups()
        ha_ip_pool = self._get_ha_data(ha_groups, ne_pk, 'subnet')
        ha_subnet_mask = self._get_ha_data(ha_groups, ne_pk, 'mask')
        ha_vlan_start = self._get_ha_data(ha_groups, ne_pk, 'vlanStart')
        ha_intf = self._get_ha_data(ha_groups, ne_pk, 'haIf')
        ha_intf_peer = self._get_ha_data(ha_groups, peer_ne_pk, 'haIf')
        this_device_ha_intf_data = self._ha_interface_label_mapping(deployment_info, ha_intf)
        deployment_info_peer_device = orch.get_appliance_deployment(ne_pk=peer_ne_pk)
        ha_peer_ha_intf_data = self._ha_interface_label_mapping(deployment_info_peer_device, ha_intf_peer)
        ha_label_order = self._ha_interface_label_order(this_device_ha_intf_data, ha_peer_ha_intf_data)
        # Get and append outbound, inbound, segment, and zone to existing data structure -> vlan_label_pairs_sorted_peer_device
        for label_entry in this_device_ha_intf_data:
            if label_entry['name'] != 'Unknown':
                label_to_search = self._find_label_id_by_name(this_device_ha_intf_data, label_entry['name'])
                outbound_inbound_shaper = self._ha_peer_interface_traffic_shaper(deployment_info, ha_intf, label_to_search)
                # add new key value pairs to data structure
                label_entry['outbound'] = outbound_inbound_shaper[0]
                label_entry['inbound'] = outbound_inbound_shaper[1]
                label_entry['segment'] = 'Default'  # TODO: When is this not Default?
                # Get zone ID for peer ha device by looking at ha interface label mapping
                # Multiple zone IDs can be designated for a single zone name - see deployment_info.sysConfig.zones
                zone_id = self._find_zone_id_by_label_and_ifname(deployment_info, this_device_ha_intf_data, label_entry['name'],
                                                                 ha_intf)
                # Find zone name by using label id on ha sub-interface
                zone_name = self._find_zone_name_by_id(deployment_info_peer_device, zone_id)
                if zone_name is None:
                    zone_name = ''
                label_entry['zone'] = zone_name
        # Pack variables for the HA config and put into dict to be used in Jinja template:
        ha_config = {
            'haPeerHostname': peer_hostname,
            'haIpPool': ha_ip_pool,
            'haSubnetMask': ha_subnet_mask,
            'haVlanStart': ha_vlan_start,
            'haInterface': ha_intf,
            'haInterfaceOrder': ha_label_order,
            'haPeerInterfaceInfo': this_device_ha_intf_data,
        }
        return ha_config


    def _get_ha_data(self, data: dict | list, search_ne_pk: str, search_data_field: str) -> any:
        """
        Recursively search through a nested structure to find the specified field.
        """
        if isinstance(data, dict):  # If the current data is a dictionary
            for key, value in data.items():
                # 1. Check if the current key matches the search field (top-level/list fields case)
                if key == search_data_field:
                    return value
                # 2. Check if this is an 'appliances' list and match `nePk`
                if key == "appliances" and isinstance(value, list):
                    for appliance in value:
                        if appliance.get("nePk") == search_ne_pk:  # Match `nePk` inside appliance
                            if search_data_field in appliance:
                                return appliance.get(search_data_field)
                # 3. Recurse through nested dictionaries
                result = self._get_ha_data(value, search_ne_pk, search_data_field)
                if result is not None:
                    return result
        elif isinstance(data, list):  # If the current data is a list, iterate through it
            for item in data:
                result = self._get_ha_data(item, search_ne_pk, search_data_field)
                if result is not None:
                    return result
        return None  # Return None if the value was not found


    def _ha_interface_label_order(self, vlan_label_pairs_sorted, vlan_label_pairs_sorted_peer_device) -> str:
        """
        The `ha_interface_label_order` function creates an ordered list of HA interface labels common to both devices.

        It does the following:
        1. Combines the HA interface label mappings (`vlan_label_pairs_sorted` and `vlan_label_pairs_sorted_peer_device`)
           from paired HA devices into one aggregated list.
        2. If a label is marked as "Unknown", it tries to replace it with a matching label from the peer device based on the
           `vlan` value.
        3. Generates a comma-separated string of ordered label names from this aggregated list.

        The function returns the ordered list of HA interface labels as a string.

        """
        # Create the aggregated complete list of HA interface to label mappings common between both devices
        aggregated_ha_interface_labels = []
        for item in vlan_label_pairs_sorted:
            if item['name'] == 'Unknown':  # Check if name is "Unknown"
                # Find a matching dictionary in list2 based on 'vlan' key
                replacement = next(
                    (entry for entry in vlan_label_pairs_sorted_peer_device if entry['vlan'] == item['vlan']), None)
                aggregated_ha_interface_labels.append(
                    replacement if replacement else item)  # Replace if found, otherwise keep the original
            else:
                aggregated_ha_interface_labels.append(item)  # Keep the original if "name" is not "Unknown"
        # get and return ordered label names
        ha_label_ordered_list = ",".join([item['name'] for item in aggregated_ha_interface_labels])
        return ha_label_ordered_list


    def _ha_interface_label_mapping(self, deployment_info, ha_intf) -> list[dict]:
        """
        The `ha_interface_label_mapping` function maps VLANs and labels of a specified HA interface to their corresponding
        names.

        It performs the following:
        1. Retrieves a mapping of label IDs to their names from the `deployment_info`.
        2. Extracts VLAN and label data for the specified interface (`ha_intf`).
        3. Sorts the extracted data by the VLAN value.
        4. Maps each label ID to its name based on the retrieved mapping. If no match is found, the name defaults to
           "Unknown".
        5. Returns a sorted list of dictionaries, each containing the VLAN, label, and name for the specified HA interface.

        The function provides a structured representation of HA interface labels to be used in further operations.
        """

        # Get ID to WAN Label mappings
        id_to_wan_label_mapping = deployment_info['sysConfig']['ifLabels']['wan']
        # Convert id_name_mapping to a dictionary for efficient lookups
        id_to_wan_label_mapping = {item['id']: item['name'] for item in id_to_wan_label_mapping}
        # Extract `vlan` and `label` for 'ifName' == 'wan1'
        vlan_label_pairs = []
        for interface in deployment_info["modeIfs"]:
            if interface["ifName"] == ha_intf:  # Check if the ifName is 'wan1'
                for ip in interface["applianceIPs"]:  # Iterate over applianceIPs
                    vlan_label_pairs.append({
                        "vlan": ip.get("vlan"),  # Get the vlan
                        "label": ip.get("label")  # Get the label
                    })
        # Output the result
        # Sort the list of dictionaries by 'vlan' key
        vlan_label_pairs_sorted = sorted(vlan_label_pairs, key=lambda x: x["vlan"])
        # Output the sorted result
        # Map 'label' in vlan_label_pairs_sorted to the corresponding 'name'
        for pair in vlan_label_pairs_sorted:
            label_id = pair.get("label")
            # Only try to map if label exists and is not empty
            pair["name"] = id_to_wan_label_mapping.get(label_id, "Unknown")  # Default to "Unknown" if no match is found
        return vlan_label_pairs_sorted


    def _ha_peer_interface_traffic_shaper(self, deployment_info: dict, ha_intf: str, if_label_id: int) -> list:
        """
        The `ha_peer_interface_traffic_shaper` function retrieves traffic shaper values (outbound and inbound bandwidth
        limits) for a specific HA sub-interface and label.

        Steps:
        1. Loops through the interface configurations (`modeIfs`) in the `deployment_info`.
        2. Identifies the specified HA interface (`ha_intf`).
        3. Searches for matching label IDs (`if_label_id`) in the interface's `applianceIPs`.
        4. If a match is found and traffic shaper values (`maxBW`) are defined, it extracts the outbound and inbound
           bandwidth limits.
        5. Returns a list of two values: `[outbound, inbound]`. Returns an empty list if no matches or traffic shaper values
           are found.

        This function is used to obtain bandwidth limit settings for a specific sub-interface and label on an HA interface.
        """
        # label_num is the id value e.g. 7, not the name of the label e.g. 'INET1'
        shaper_values = [] # [outbound, inbound]
        for mode_if in deployment_info["modeIfs"]:
            if mode_if["ifName"] == ha_intf:
                # Iterate through the 'applianceIPs' list
                for ip_data in mode_if["applianceIPs"]:
                    if ip_data.get("label") == str(if_label_id) and "maxBW" in ip_data and "inbound" in ip_data["maxBW"]:
                        shaper_values.append(ip_data["maxBW"]["outbound"])
                        shaper_values.append(ip_data["maxBW"]["inbound"])
        if len(shaper_values) == 0:
            return []
        return shaper_values

    # Function to find the label based on the name
    def _find_label_id_by_name(self, data, name_to_find):
        """
        The `find_label_id_by_name` function searches for a label ID associated with a specific name in a given dataset.

        Steps:
        1. Loops through the provided `data` (a list of dictionaries).
        2. Checks each dictionary for a `name` key matching the specified `name_to_find`.
        3. If a match is found, it returns the corresponding `label` value.
        4. If no match is found, it returns `None`.

        This function is used to retrieve the label ID for a specific name.
        """
        for item in data:
            if item.get('name') == name_to_find:  # Match the name
                return item.get('label')  # Return the label
        return None  # Return None if no matching name is found


    def _find_zone_name_by_id(self, deployment_info: dict, zone_id: str | int) -> str | None:
        zones = deployment_info.get("sysConfig", {}).get("zones", [])
        for zone in zones:
            if zone.get("id") == str(zone_id):  # Convert ID to string for comparison
                return zone.get("name")
        return None  # Return None if no match is found


    # Function to find zone by 'label' and 'ifName'
    def _find_zone_id_by_label_and_ifname(self, deployment_info: dict, data: list[dict], label_name: str, if_name: str) -> str | None:
        """
        The `find_zone_name_by_id` function retrieves the name of a zone based on its ID from the provided deployment
        information.

        Steps:
        1. Extracts the list of zones from the `deployment_info`.
        2. Iterates through each zone in the list.
        3. Checks if the `id` of the zone matches the given `zone_id` (converted to a string for comparison).
        4. If a match is found, it returns the corresponding `name` of the zone.
        5. If no match is found, it returns `None`.

        This function is useful for finding the zone name associated with a specific zone ID.
        """

        # find the label id by name
        label_id = self._find_label_id_by_name(data, label_name)

        # Access the "modeIfs" array from deployment_info
        mode_ifs = deployment_info.get("modeIfs", [])

        for interface in mode_ifs:
            # Check if 'ifName' matches
            if interface.get("ifName") == if_name:
                appliance_ips = interface.get("applianceIPs", [])
                # Iterate over 'applianceIPs' to find a matching 'label'
                for ip_data in appliance_ips:
                    if ip_data.get("label") == label_id:
                        return ip_data.get("zone")  # Return the 'zone' value if found
        return None  # Return None if no match is found


    def _is_field_present(self, data, field):
        """
        Recursively checks if a specific field exists in a nested structure.
        """
        if isinstance(data, dict):
            if field in data:
                return True
            # Recursively check nested dictionaries
            for value in data.values():
                if self._is_field_present(value, field):
                    return True
        elif isinstance(data, list):
            # Recursively check each item in the list
            for item in data:
                if self._is_field_present(item, field):
                    return True
        return False  # Return False if the field is not found


