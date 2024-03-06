# This automation workflow is meant as an interim solution for
# EdgeConnect customers looking to automate third-party tunnels
# to HPE SSE solution (formerly Axis Security) prior to the
# automation being built-in to Orchestrator
# This is not meant for ongoing maintenance, but rather, bulk
# initial connectivity

# Link to sdwan techdoc for manual integration steps
# https://www.arubanetworks.com/website/techdocs/sdwan-PDFs/integrations/int_ECSSE(Axis)-EC_latest.pdf

import argparse
import getpass
import logging
import os
import re
import time
from logging.handlers import RotatingFileHandler

import requests
from config_vars import config_vars
from sse_mgmt_auth import sse_mgmt_auth

from pyedgeconnect import Orchestrator


def filter_appliances(appliances) -> list:
    # Create list of appliance id's (nepk) to be
    # associated with new service
    target_appliances = []

    # User argument to filter what appliances will be associated to
    # the Service Orchestration service
    appliance_filter = vars(args)["appliance_filter"]
    # Assign all appliances
    if appliance_filter == "all":
        for appliance in appliances:
            target_appliances.append(appliance["id"])

    # Filter appliance list for appliances associated to
    # specified region
    elif appliance_filter[:7] == "region:":
        region = appliance_filter[7:]
        region_association = orch.get_region_appliance_association()
        region_appliances = []
        for region_appliance_id in region_association:
            if region_association[region_appliance_id]["regionName"] == region:
                region_appliances.append(region_appliance_id)
        for appliance in appliances:
            if appliance["id"] in region_appliances:
                target_appliances.append(appliance["id"])
        if len(target_appliances) == 0:
            raise ValueError(
                f"""

                No appliances found for region specified: {region}
                """
            )

    # Filter appliance list for single appliance matching
    # specified hostname
    elif appliance_filter[:9] == "hostname:":
        appliance_hostname = appliance_filter[9:]
        for appliance in appliances:
            if appliance["hostName"] == appliance_hostname:
                target_appliances.append(appliance["id"])
        if len(target_appliances) == 0:
            raise ValueError(
                f"""

                No appliances found with hostname specified: {appliance_hostname}
                """
            )
    else:
        raise ValueError(
            f"""

            Appliance Filter argument (-af) must have valid value
                `all`
                `hostname:<appliance_hostname>`
                `region:<region_name>`

            Value provided:
            {appliance_filter}
                """
        )

    return target_appliances


# Parse runtime arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-af",
    "--appliance_filter",
    help="Filter which EdgeConnect appliances are used to associate to Service Orchestration and/or configure SSE tunnels for, acceptable values are `all`, `hostname:<appliance_hostname>`, or `region:<region_name>`",
    type=str,
    required=True,
)
parser.add_argument(
    "-cso",
    "--configure_service_orchestration",
    help="Create new service orchestration service in Orchestrator per configuration variables in config_vars.py",
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-as",
    "--associate_service",
    help="Associate service remote endpoints for existing service to appliances",
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-sse",
    "--configure_sse",
    help="Configure locations and tunnels on SSE portal for existing service and appliances",
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-o",
    "--orch",
    help="specify Orchestrator URL",
    type=str,
)
parser.add_argument(
    "-ssew",
    "--sse_workspace",
    help="specify SSE workspace name",
    type=str,
)
parser.add_argument(
    "-ll",
    "--log_level",
    help="specify logging level of workflow, will not log to file if not specified, e.g. INFO, WARNING, ERROR",
    type=str,
)
args = parser.parse_args()

start_time = time.time()

# Setup log settings for messages and errors
if vars(args)["log_level"] is not None:
    log_level = vars(args)["log_level"]
elif os.getenv("LOG_LEVEL") is not None:
    log_level = os.getenv("LOG_LEVEL")
else:
    log_level = None
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
local_log_directory = "logging/"
if not os.path.exists(local_log_directory):
    os.makedirs(local_log_directory)
log_file_handler = RotatingFileHandler(
    f"{local_log_directory}ec-service_orch_sse.log",
    maxBytes=1000000,
    backupCount=2,
)
# Set logging severity level from environment variable
log_file_handler.setFormatter(formatter)
if log_level == "CRITICAL":
    logger.setLevel(logging.CRTICAL)
elif log_level == "ERROR":
    logger.setLevel(logging.ERROR)
elif log_level == "WARNING":
    logger.setLevel(logging.WARNING)
elif log_level == "INFO":
    logger.setLevel(logging.INFO)
elif log_level == "DEBUG":
    logger.setLevel(logging.DEBUG)
elif log_level is None:
    logger.disabled = True
logger.addHandler(log_file_handler)


# Set Orchestrator FQDN/IP via arguments, environment variable,
# or user input
if vars(args)["orch"] is not None:
    orch_url = vars(args)["orch"]
elif os.getenv("ORCH_URL") is not None:
    orch_url = os.getenv("ORCH_URL")
else:
    orch_url = input("Orchstrator IP or FQDN: ")

# Set Orchestrator API Key via environment variable or user input
if os.getenv("ORCH_API_KEY") is not None:
    orch_api_key = os.getenv("ORCH_API_KEY")
else:
    orch_api_key_input = getpass.getpass(
        "Orchstrator API Key (enter to skip): "
    )
    if len(orch_api_key_input) == 0:
        orch_api_key = None
        # Set user and password if present in environment variable
        orch_user = os.getenv("ORCH_USER")
        orch_pw = os.getenv("ORCH_PASSWORD")
    else:
        orch_api_key = orch_api_key_input

# Instantiate Orchestrator with ``log_console`` enabled for
# printing log messages to terminal
orch = Orchestrator(
    orch_url,
    api_key=orch_api_key,
    log_console=False,
    verify_ssl=False,
)

# If not using API key, login to Orchestrator with username/password
if orch_api_key is None:
    # If username/password not in environment variables, prompt user
    if orch_user is None:
        orch_user = input("Enter Orchestrator username: ")
        orch_pw = getpass.getpass("Enter Orchestrator password: ")
    # Check if multi-factor authentication required
    mfa_prompt = input("Are you using MFA for this user (y/n)?: ")
    if mfa_prompt == "y":
        orch.send_mfa(orch_user, orch_pw, temp_code=False)
        token = input("Enter MFA token: ")
    else:
        token = ""
    # Login to Orchestrator
    confirm_auth = orch.login(orch_user, orch_pw, mfacode=token)
    # Check that user/pass authentication works before proceeding
    if confirm_auth:
        pass
    else:
        print("Authentication to Orchestrator Failed")
        logger.critical("Authentication to Orchestrator Failed")
        exit()
# If API key specified, check that key is valid before proceeding
else:
    confirm_auth = orch.get_orchestrator_hello()
    if confirm_auth != "There was an internal server error.":
        pass
    else:
        print("Authentication to Orchestrator Failed")
        logger.critical("Authentication to Orchestrator Failed")
        exit()

# Set SSE workspace name via arguments, environment variable,
# or user input
if vars(args)["sse_workspace"] is not None:
    sse_workspace = vars(args)["sse_workspace"]
elif os.getenv("SSE_WORKSPACE") is not None:
    sse_workspace = os.getenv("SSE_WORKSPACE")
else:
    sse_workspace = input("SSE Workspace name: ")

# Set SSE portal admin username and password
# via environment variable or user input
if os.getenv("SSE_USER") is not None:
    sse_user = os.getenv("SSE_USER")
else:
    sse_user = input("Enter SSE admin username: ")
if os.getenv("SSE_PW") is not None:
    sse_password = os.getenv("SSE_PW")
else:
    sse_password = getpass.getpass("Enter SSE admin password: ")


# Constant values for Remote Endpoints and IPSLA target
SSE_PRIMARY_REMOTE_ENDPOINT = "ipsec-proxy-geo.axisapps.io"
SSE_BACKUP_REMOTE_ENDPOINT = "ipsec-proxy-secondary-geo.axisapps.io"
IPSLA_PROBE_ENDPOINT = "http://sp-ipsla.silverpeak.cloud"


# Validate Orchestrator version to support variable IKEv2 ID's
orch_info = orch.get_orchestrator_server_brief()
orch_release = orch_info["release"]
major = int(orch_release.split(".")[0])
minor = int(orch_release.split(".")[1])
orch_version = major + minor / 10
if orch_version < 9.2:
    raise ValueError(
        f"""
        This code example requires Orchestration version 9.2+

        Orchestrater is currently running {orch_release}
        """
    )

# User arguments for service name and WAN labels to use
service_name = config_vars["service_name"]
service_prefix = config_vars["service_prefix"]
primary_wan_labels = config_vars["primary_labels"]
backup_wan_labels = config_vars["backup_labels"]
# LAN Labels or interface names for IPSLA source
ipsla_source_interface = config_vars["ipsla_source"]
# Local IKE ID FQDN for IPSEC Tunnels
service_ike_id_fqdn = config_vars["service_ike_id_fqdn"]
# Lookup if tunnel psk provided, if not prompt for user entry
tunnel_psk = os.getenv("TUNNEL_PSK")
if tunnel_psk is None:
    tunnel_psk = getpass.getpass("Enter IPSEC Tunnel PSK: ")

# Validate user-specified configuration data
# No formatting validation performed on ipsla source interface
# or service ike identifier fqdn
if type(service_name) is not str or len(service_name) == 0:
    raise TypeError(
        f"""

        Service name must be a string with 1 or more characters
        Value provided:
        {service_name}
        Type provided:
        {type(service_name)}"""
    )
if type(service_prefix) is not str or len(service_prefix) == 0:
    raise TypeError(
        f"""

        Service prefix must be a string with 1 or more characters
        Value provided:
        {service_prefix}
        Type provided:
        {type(service_prefix)}"""
    )
if type(primary_wan_labels) is not list:
    raise TypeError(
        f"""

        Primary WAN labels must be provided in list[str] format
        Value provided:
        {primary_wan_labels}"""
    )
elif len(primary_wan_labels) == 0:
    raise ValueError(
        f"""

        No Primary WAN labels were specified, must specify at least one Primary WAN label
        Value provided:
        {primary_wan_labels}"""
    )
if type(backup_wan_labels) is not list:
    raise TypeError(
        f"""

        Backup WAN Lables must be provided in list[str] format
        Value provided:
        {backup_wan_labels}
        Type provided:
        {type(backup_wan_labels)}"""
    )
if type(ipsla_source_interface) is not str or len(ipsla_source_interface) == 0:
    raise TypeError(
        f"""

        IPSLA source interface must be a string with 1 or more characters
        Value provided:
        {ipsla_source_interface}
        Type provided:
        {type(ipsla_source_interface)}"""
    )
if type(service_ike_id_fqdn) is not str or len(service_ike_id_fqdn) == 0:
    raise TypeError(
        f"""

        Service IKE identifier fqdn must be a string with 1 or more characters
        e.g., "sse.customer.lab"
        Value provided:
        {service_ike_id_fqdn}
        Type provided:
        {type(service_ike_id_fqdn)}"""
    )

# Get WAN & LAN labels from Orchestrator to find label id values
orch_wan_labels = orch.get_interface_labels_by_type(
    label_type="wan",
    active=True,
)
orch_lan_labels = orch.get_interface_labels_by_type(
    label_type="lan",
    active=True,
)

# Organize label id values for service orchestration
primary_label_ids = []
backup_label_ids = []

# List of names of valid WAN label names and target
# label names specified in config file
orch_wan_label_names = [orch_wan_labels[x]["name"] for x in orch_wan_labels]
orch_lan_label_names = [orch_lan_labels[x]["name"] for x in orch_lan_labels]

# All WAN labels in use for SSE service
target_label_names = primary_wan_labels + backup_wan_labels

# Identify if any labels specified in target labels aren't configured
# on Orchestrator
missing_labels = []
for label_id in target_label_names:
    if label_id not in orch_wan_label_names:
        missing_labels.append(label_id)

if len(missing_labels) > 0:
    raise ValueError(
        f"""

        One or more labels specified was not found in Orchestrator!

        Primary labels provided:
        {primary_wan_labels}
        Backup labels provided:
        {backup_wan_labels}

        These labels are not valid:
        {missing_labels}

        Valid WAN labels currently defined in Orchestrator:
        {orch_wan_label_names}
"""
    )

# Nest WAN label ID's in list for reference of service orchestration
# E.g., primary_label_ids = ["1","2"] and backup_label_ids = ["3"]
# Later allows assembling as [["1","2"],["3"]]

# Also assemble flat list of all ID's for reference in deployment check
# E.g., in_use_labels == ["1","2","3"]
in_use_labels = []
for label_id in orch_wan_labels:
    if orch_wan_labels[label_id]["name"] in primary_wan_labels:
        primary_label_ids.append(label_id)
        in_use_labels.append(label_id)
    elif orch_wan_labels[label_id]["name"] in backup_wan_labels:
        backup_label_ids.append(label_id)
        in_use_labels.append(label_id)

# Parameters to execute particular portions of the workflow
configure_new_service_orchestration = vars(args)[
    "configure_service_orchestration"
]
associate_service_orchestration = vars(args)["associate_service"]
configure_sse = vars(args)["configure_sse"]

# Configuring new Service Orchestration service
if configure_new_service_orchestration:
    print("Creating new Service Orchestration in Orchestrator")
    logger.info("Creating new Service Orchestration in Orchestrator")

    # Check if a service with the same name already exists
    existing_services = orch.get_service_orchestration_all_names_to_ids()

    if service_name in existing_services.values():
        raise ValueError(
            f"""

            A Service Orchestration service with the name
            {service_name} already exists in Orchestrator

            Either skip creating new Service Orchestration
            and associate the existing service or use
            new unique name for new service.
        """
        )

    # Create new Service Orchestration in Orch
    create_service = orch.add_new_service_orchestration(
        service_name=service_name,
        service_prefix=service_prefix,
        bio_breakout=1,
    )

    # If response contains service ID it was sucessfully created
    if create_service.get("serviceId") is not None:
        logger.info(f"Service Orchestration Service {service_name} created")

        service_id = create_service["serviceId"]

        # Configure WAN labels to use for service
        set_labels = orch.set_service_orchestration_labels(
            service_id=service_id,
            labels=[primary_label_ids, backup_label_ids],
        )
        if set_labels:
            logger.info(f"WAN labels associated to {service_name}")
        else:
            logger.error(f"WAN labels failed to associate to {service_name}")

        # Configure Tunnel settings for service
        set_tunnel_settings = orch.set_service_orchestration_tunnel_settings(
            service_id=service_id,
            ike_id_format=f"%hostname%_%label%@{service_ike_id_fqdn}",
        )
        if set_tunnel_settings:
            logger.info(f"Tunnel settings configured for {service_name}")
        else:
            logger.error(f"Tunnel settings failed to apply for {service_name}")
        # Configure IPSLA settings for service
        set_ipsla = orch.set_service_orchestration_ipsla_settings(
            service_id=service_id,
            source_interface=ipsla_source_interface,
        )
        if set_ipsla:
            logger.info(f"IPSLA settings configured for {service_name}")
        else:
            logger.error(f"IPSLA settings failed to apply to {service_name}")

        # Configure secondary remote endpoint for service
        backup_endpoint = orch.add_service_orchestration_remote_endpoints(
            service_id=service_id,
            remote_endpoints=[
                {
                    "remoteEndpointName": "EC-SSE-Secondary",
                    "labelId": "any",
                    "ipAddress": SSE_BACKUP_REMOTE_ENDPOINT,
                    "preSharedKey": tunnel_psk,
                    "probeIpAddress": IPSLA_PROBE_ENDPOINT,
                },
            ],
        )
        if backup_endpoint:
            logger.info(
                f"Backup remote endpoint configured for {service_name}"
            )
        else:
            logger.error(
                f"Failed to configure backup remote endpoint for {service_name}"
            )
        # Retrieve remoteEndpointId from newly created endpoint
        endpoints = orch.get_service_orchestration_remote_endpoints(
            service_id=service_id
        )
        backup_endpoint_id = endpoints["remoteEndpoints"][0][
            "remoteEndpointId"
        ]

        # Configure primary remote endpoint for service
        primary_endpoint = orch.add_service_orchestration_remote_endpoints(
            service_id=service_id,
            remote_endpoints=[
                {
                    "remoteEndpointName": "EC-SSE-Primary",
                    "labelId": "any",
                    "ipAddress": SSE_PRIMARY_REMOTE_ENDPOINT,
                    "preSharedKey": tunnel_psk,
                    "probeIpAddress": IPSLA_PROBE_ENDPOINT,
                    "backupEndpointId": backup_endpoint_id,
                },
            ],
        )
        if primary_endpoint:
            logger.info(
                f"Primary remote endpoint configured for {service_name}"
            )
        else:
            logger.error(
                f"Failed to configure backup remote endpoint for {service_name}"
            )

    else:
        logger.critical(f"Failed to create {service_name}")
        logger.critical(f"Create service response: {create_service}")
        raise RuntimeError(
            f"""
            Failed to create new service

            Service name:
            {service_name}

            Create service response:
            {create_service}
            """
        )

# If not configuring new Service Orchestration service, get existing
# configured services to find specified service details
else:
    service_id = None
    existing_services = orch.get_service_orchestration_all_names_to_ids()
    for service in existing_services:
        if existing_services[service] == service_name:
            service_id = service
    if service_id is None:
        raise ValueError(
            f"""
            A Service Orchestration service with the name
            {service_name} does not exist in Orchestrator

            Either create new Service Orchestration or check
            spelling of existing service name.
        """
        )

# Retrieve remote endpoint id's for association to appliances
endpoints = orch.get_service_orchestration_remote_endpoints(
    service_id=service_id,
)

for endpoint in endpoints["remoteEndpoints"]:
    if endpoint["ipAddress"] == SSE_PRIMARY_REMOTE_ENDPOINT:
        primary_endpoint_id = endpoint["remoteEndpointId"]

# Get appliance inventory from Orchestrator
appliances = orch.get_appliances()

# Filter appliance inventory for target appliances based on
# runtime argument "appliance_filter"
target_appliances = filter_appliances(appliances)

# Get EdgeHA Appliance Lists
# Hostname of first appliance in EdgeHA pair used for SSE location name
# for appliances that are in EdgeHA group with no Site Name configured
edge_ha_appliances = {}
appliance_hostnames = {}
for appliance in appliances:
    appliance_hostnames[appliance["id"]] = appliance["hostName"]

edge_ha_groups = orch.get_ha_groups()

for ha_group in edge_ha_groups:
    ec1 = edge_ha_groups[ha_group]["appliances"][0]["nePk"]
    ec2 = edge_ha_groups[ha_group]["appliances"][1]["nePk"]

    ec1_hostname = appliance_hostnames[ec1]

    edge_ha_appliances[ec1] = ec1_hostname
    edge_ha_appliances[ec2] = ec1_hostname

# Put appliance Site and Hostname information for each appliance in
# reference dictionary if configured
ec_site_mapping = {}
for appliance in appliances:
    # If appliance has a site defined this will be used for
    # location name in SSE portal
    if appliance["site"] is not None:
        ec_site_mapping[appliance["id"]] = {
            "site": appliance["site"],
            "hostname": appliance["hostName"],
        }
    # If appliance does not have a site configured and is in an
    # EdgeHA group, Site Name will be one of the two appliance hostnames
    # with a prefix of EdgeHA_<hostname1> for both appliances
    elif appliance["id"] in edge_ha_appliances:
        ec_site_mapping[appliance["id"]] = {
            "site": f"EdgeHA_{edge_ha_appliances[appliance['id']]}",
            "hostname": appliance["hostName"],
        }
    # Else assume appliance is a single appliance at a location with
    # no Site Name configured and will use the hostname as location
    # name in SSE portal
    else:
        ec_site_mapping[appliance["id"]] = {
            "site": appliance["hostName"],
            "hostname": appliance["hostName"],
        }

# Get existing associations to avoid removing
# them when adding new associations
endpoint_association = orch.get_service_orchestration_appliance_association(
    service_id=service_id
)

# Add net-new appliances to endpoint association to primary endpoint
# The backup endpoint is defined and will be auto-discovered by
# appliance through primary endpoint
for appliance_id in target_appliances:
    if primary_endpoint_id not in endpoint_association:
        endpoint_association[primary_endpoint_id] = [appliance_id]
    elif appliance_id not in endpoint_association[primary_endpoint_id]:
        endpoint_association[primary_endpoint_id].append(appliance_id)

# Associating appliances to Service Orchestration service
if associate_service_orchestration:
    print(f"Associating EdgeConnect appliances to {service_name}")
    logger.info(f"Associating EdgeConnect appliances to {service_name}")

    # Update appliance endpoint association
    # This will kick off an orchestration task in Orchestrator to
    # tell each appliance the details of building tunnels to the new
    # service endpoints
    associate_result = orch.set_service_orchestration_appliance_association(
        service_id=service_id,
        association=endpoint_association,
    )

    if associate_result:
        # Check Orchestrator if configuration entry
        # present for appliances
        # Check every 5 seconds until all expected
        # new appliances have completed orchestration
        print(
            f"Appliances associated to {service_name}, orchestration in progress"
        )
        logger.info(
            f"Appliances associated to {service_name}, orchestration in progress"
        )
    else:
        print(f"Appliances failed to associate to {service_name}")
        logger.error(f"Appliances failed to associate to {service_name}")


configure_sse = vars(args)["configure_sse"]


# Configure SSE side of IPSEC tunnels for targeted appliances
if configure_sse:  # noqa: C901
    sse_mgmt = sse_mgmt_auth(sse_workspace, sse_user, sse_password)
    sse_mgmt_base_url = sse_mgmt["mgmt_base_url"]
    sse_mgmt_session = sse_mgmt["mgmt_session"]
    sse_tenant_id = sse_mgmt["tenant_id"]

    end_time = time.time()
    total_time = int(end_time - start_time)
    print(f"TOTAL TIME: {total_time}")
    print("Getting existing locations and tunnels in SSE")

    # Get existing SSE locations configured
    location_request = sse_mgmt_session.get(
        f"{sse_mgmt_base_url}/Location",
        allow_redirects=False,
    )
    sse_locations_json = location_request.json()
    existing_sse_locations = {}
    for location in sse_locations_json:
        existing_sse_locations[location["name"]] = location

    # Get existing SSE tunnels configured
    tunnel_request = sse_mgmt_session.get(
        f"{sse_mgmt_base_url}/Tunnel",
        allow_redirects=False,
    )
    sse_tunnels_json = location_request.json()
    existing_sse_tunnels = {}
    for tunnel in tunnel_request.json():
        existing_sse_tunnels[tunnel["name"]] = tunnel

    ec_tunnel_list = []
    completed_ipsec_tunnels = []
    ec_tunnel_identifiers = {}

    end_time = time.time()
    total_time = int(end_time - start_time)
    print(f"TOTAL TIME: {total_time}")
    print(
        "Gathering deployment information from target EdgeConnect appliances"
    )
    # Workflow adding tunnels from EdgeConnect/Orchestrator

    # Get deployment information from each target EdgeConnect
    # appliance to identify interfaces with labels specified for
    # service
    appliance_deployments = orch.get_all_appliance_deployment()
    for appliance_id in target_appliances:
        try:

            time.sleep(0.2)

            if (
                isinstance(appliance_deployments, dict)
                and appliance_id in appliance_deployments
            ):
                for interface in appliance_deployments[appliance_id][
                    "wanInterfaces"
                ]:
                    # Lookup corresponding label name for label id
                    # Added to tracking list to validate matches
                    # for IPSLA source defined
                    label_id = interface["label"]
                    label_name = orch_wan_labels[label_id]["name"]

                    # For the WAN interfaces, create object for
                    # local IKE identifier to be referenced for defining
                    # tunnel on SSE portal
                    if interface["wanSide"] is True:
                        if label_id in in_use_labels:
                            hostname = ec_site_mapping[appliance_id][
                                "hostname"
                            ]
                            label_name = orch_wan_labels[label_id]["name"]
                            local_ike_id = f"{hostname}_{label_name}@{service_ike_id_fqdn}"
                            ec_tunnel_identifiers[
                                f"{appliance_id}_{label_id}_{primary_endpoint_id}"
                            ] = {
                                "localIkeIdentifier": local_ike_id,
                            }
                            ec_tunnel_list.append(local_ike_id)

        except Exception as e:
            print(f"Failed to retrieve deployment for {appliance_id}")
            print(e)
            pass

    end_time = time.time()
    total_time = int(end_time - start_time)
    print(f"TOTAL TIME: {total_time}")
    print("Configuring locations and tunnels in SSE")

    for existing_tunnel in existing_sse_tunnels:
        sse_tunnel_ike_id = existing_sse_tunnels[existing_tunnel]["localId"]

        if sse_tunnel_ike_id in ec_tunnel_list:
            completed_ipsec_tunnels.append(sse_tunnel_ike_id)

    for ec_tunnel in ec_tunnel_identifiers:
        # If tunnel not already configured, add to SSE portal
        if (
            ec_tunnel_identifiers[ec_tunnel]["localIkeIdentifier"]
            not in completed_ipsec_tunnels
        ):
            ne_pk = f"{ec_tunnel.split('.NE')[0]}.NE"
            appliance_ike_identifier = ec_tunnel_identifiers[ec_tunnel][
                "localIkeIdentifier"
            ]
            site = ec_site_mapping[ne_pk]["site"]

            location_name = f"EdgeConnect_{site}"

            if appliance_ike_identifier not in completed_ipsec_tunnels:
                # Create new location in SSE if doesn't already exist
                if location_name not in existing_sse_locations:
                    location_data = {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "name": location_name,
                        "tenantId": sse_tenant_id,
                        "subLocations": [],
                    }

                    print(f"Creating new location: {location_name}")
                    new_location = sse_mgmt_session.post(
                        f"{sse_mgmt_base_url}/Location",
                        allow_redirects=False,
                        json=location_data,
                    )

                    if new_location.status_code == 201:
                        existing_sse_locations[new_location.json()["name"]] = (
                            new_location.json()
                        )
                        sse_commit_required = True

                # Create new IPSEC tunnel definition in SSE portal
                tunnel_prefix = appliance_ike_identifier.split("@")[0]

                tunnel_data = {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "name": f"EdgeConnect_{tunnel_prefix}",
                    "tenantId": sse_tenant_id,
                    "locationId": existing_sse_locations[location_name]["id"],
                    "localId": appliance_ike_identifier,
                    "preSharedKey": tunnel_psk,
                    "location": {
                        "subLocations": existing_sse_locations[location_name][
                            "subLocations"
                        ],
                        "tunnels": [],
                        "name": existing_sse_locations[location_name]["name"],
                        "tenantId": sse_tenant_id,
                        "id": existing_sse_locations[location_name]["id"],
                    },
                }

                new_tunnel = sse_mgmt_session.post(
                    f"{sse_mgmt_base_url}/Tunnel",
                    allow_redirects=False,
                    json=tunnel_data,
                )
                sse_commit_required = True

                completed_ipsec_tunnels.append(appliance_ike_identifier)

    # Avoids accidental commits of other pending changes by other admins
    # that are still pending when this automation runs
    if sse_commit_required:
        print(
            """
              Commit is required to apply changes in SSE Portal

              Please login and review pending changes before committing
              as there may be other pending changes from other admins
              that will be committed along with those made by this
              workflow.

              An example script to execute a Commit with the API can
              be found in commit_sse.py
              """
        )

    else:
        print(
            """
              No changes were made by this workflow in the SSE portal

              Review if changes have been committed or are still
              pending commit to confirm if they are ready to be applied
              """
        )

    # Logout from Axis Management API
    sse_mgmt_session.get("https://manage.axissecurity.com/Account/Logout")


# If not using API key, logout from Orchestrator
if orch_api_key is None:
    orch.logout()

end_time = time.time()
total_time = int(end_time - start_time)
print(f"TOTAL TIME: {total_time}")
