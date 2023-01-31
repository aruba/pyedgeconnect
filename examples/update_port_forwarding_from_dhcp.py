import argparse
import getpass
import os

from pyedgeconnect import EdgeConnect

# Parse runtime arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-a",
    "--appliance",
    help="Appliance ip address",
    type=str,
)
parser.add_argument(
    "-l",
    "--label",
    help="Interface WAN label to check",
    type=str,
)
args = parser.parse_args()

# Set EdgeConnect FQDN/IP via arguments or user input
if vars(args)["appliance"] is not None:
    ec_url = vars(args)["appliance"]
else:
    ec_url = input("EdgeConnect IP or FQDN: ")

# Set EdgeConnect login via environment variable or user input
if os.getenv("EC_USER") is not None and os.getenv("EC_PW"):
    ec_user = os.getenv("EC_USER")
    ec_pw = os.getenv("EC_PW")
else:
    ec_user = input("EdgeConnect admin user: ")
    ec_pw = getpass.getpass("EdgeConnect admin password: ")

# Instantiate EdgeConnect with ``log_console`` enabled for
# printing log messages to terminal
ec = EdgeConnect(
    ec_url,
    log_console=True,
    verify_ssl=False,
)

ec.login(ec_user, ec_pw)

target_label = vars(args)["label"]
if target_label is None:
    target_label = input("WAN label to check (e.g. INET1): ")

# Check that a valid WAN label was specified to match for inbound port
# forwarding rules
if target_label is None:
    print("No WAN label provided to check inbound port forwarding for")
    exit()

# Get deployment detail from appliance
deployment = ec.get_appliance_deployment()

# Identify WAN label ID from label name provided by user
for wan_label in deployment["sysConfig"]["ifLabels"]["wan"]:
    if wan_label["name"] == target_label:
        label_id = wan_label["id"]
        break
    else:
        label_id = None

if label_id is None:
    print(f"WAN label {target_label} not present on {hostname}")
    exit()

# Find WAN IP address of corresponding interface with WAN label that is
# configured with DHCP
for interface in deployment["modeIfs"]:
    for subinterface in interface["applianceIPs"]:
        if subinterface["label"] == label_id and subinterface["dhcp"] is True:
            wan_ip = subinterface["ip"]
            break
        else:
            wan_ip = None

# If WAN IP found, get existing inbound port forwarding rules and update
if wan_ip is not None:

    pfw_rules = ec.get_port_forwarding_rules()

    # If WAN IP is different than the destination subnet in existing
    # port forwarded rules, update with the current WAN IP from
    # deployment
    rule_update = False
    for rule in pfw_rules:
        if rule["destSubnet"].split("/")[0] == wan_ip:
            print("WAN IP is correct in PFW rule, no change")
        else:
            rule["destSubnet"] = wan_ip + "/32"
            print("WAN IP is different in PFW rule, updating")
            rule_update = True

    if rule_update:

        ec.set_port_forwarding_rules(pfw_rules=pfw_rules)

ec.logout()
