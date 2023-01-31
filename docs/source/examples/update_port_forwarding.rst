.. update_port_forwarding:


.. important::

    The following example is more complex code than the general examples,
    automating the configuration change of existing inbound port
    forwarding rules. Using and modifying these examples requires a
    greater understanding of python functions, handling variables, and
    understanding of the data structures involved.

    Updating the inbound port forwarding rules of an EdgeConnect,
    especially with automation, should be treated with caution as a
    misconfiguration could allow unwanted traffic or block unintended
    production traffic. This code example is not meant to check the
    intent of any rules, simply show how policy can be updated in an
    automated fashion.

.. note::

    The code referenced in this document and all published examples
    with pyedgeconnect are available from the GitHub repository within the
    `examples <https://github.com/aruba/pyedgeconnect/tree/main/examples>`_
    folder. Each example script contains logic to authenticate to the
    Orchestrator as documented in the authentication example.

    Clone the repository and download the examples with:

    .. code:: bash

        $ git clone https://github.com/aruba/pyedgeconnect.git

Update Port Forwarding From DHCP
************************************

This example takes an EdgeConnect appliance with existing Inbound Port
Forwarding rules corresponding to a WAN interface with a label specified
by the user to update the destination IP address assuming it has
recently changed due to the interface being addressed via DHCP.

The client running the script communicates directly with the EdgeConnect
appliance and as such requires direct IP connectivity to the appliance.

Python Script & EdgeConnect API calls
======================================

The script will first login to the appliance, looking for
environment variables ``EC_USER`` and ``EC_PW`` for credentials, if
either are not set it will prompt the user to enter valid admin
credentials.

    .. code-block::python

        # Set EdgeConnect login via environment variable or user input
        if os.getenv("EC_USER") is not None and os.getenv("EC_PW"):
            ec_user = os.getenv("EC_USER")
            ec_pw = os.getenv("EC_PW")
        else:
            ec_user = input("EdgeConnect admin user: ")
            ec_pw = getpass("EdgeConnect admin password: ")

        # Instantiate EdgeConnect with ``log_console`` enabled for
        # printing log messages to terminal
        ec = EdgeConnect(
            ec_url,
            log_console=True,
            verify_ssl=False,
        )

        ec.login(ec_user, ec_pw)

Assuming the login is successful, the appliance Deployment is retrieved
and parsed for a WAN interface with a matching label specified by the
user and that has an IP address that has been assigned via DHCP.

    .. code-block::python

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

Finally, the destination address in the existing port forwarding rules
are compared with the current WAN IP address, and if different, are
corrected and updated to the appliance


    .. code-block::python

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

.. warning::

    In it's current form, this script is not written to handle an
    appliance with multiple dhcp addressed WAN interfaces with related
    inbound port forwarding rules. The current logic would find the
    first matching interface with the specified label and update
    all port forwarding rules for that destination IP.

Runtime arguments
^^^^^^^^^^^^^^^^^

The python script has multiple runtime arguments defined. The two
required arguments are below:

* Use ``-a`` or ``--appliance`` to specify the appliance hostname or ip
  address to connect to
* Use ``-l`` or ``--label`` to specify WAN label (e.g. ``INET1``) to
  retrieve IP information for and update destination ip addresses in
  inbound port forwarding rules

Example details
^^^^^^^^^^^^^^^^^

Prior to any changes the appliance has multiple existing inbound port
forwarding rules configured and a previous WAN IP address of
192.0.2.2/24 from dhcp as below:

    .. list-table::
        :header-rows: 1

        * - Source IP
          - Destination IP
          - Destination Port/Range
          - Protocol
          - Translated IP
        * - 0.0.0.0/0
          - 192.0.2.2/32
          - 443
          - TCP
          - 198.51.100.2
        * - 0.0.0.0/0
          - 192.0.2.2/32
          - 8443
          - TCP
          - 198.51.100.2

Assuming the WAN interface with a label of INET1 has it's WAN
address updated from dhcp, and is currently 192.0.2.40/24. Run the
script specifying the appliance's management IP address of
198.51.100.254 and the WAN label of INET1

.. code-block:: bash

    $ python update_port_forwarding_from_dhcp.py -a 198.51.100.254 -l INET1

Because the WAN ip has changed, is assigned via DHCP, and has a WAN
label of INET1, the port forwarding rules will be updated as follows:

    .. list-table::
        :header-rows: 1

        * - Source IP
          - Destination IP
          - Destination Port/Range
          - Protocol
          - Translated IP
        * - 0.0.0.0/0
          - **192.0.2.40/32**
          - 443
          - TCP
          - 198.51.100.2
        * - 0.0.0.0/0
          - **192.0.2.40/32**
          - 8443
          - TCP
          - 198.51.100.2

EdgeConnect API calls
^^^^^^^^^^^^^^^^^^^^^^^^^^

The API calls to Orchestrator (outside of authentication) used in this
example are:

* :func:`pyedgeconnect.EdgeConnect.get_appliance_deployment`
   * Retrieves appliance Deployment configuration to find interface IP
     ip addresses and interface labels
* :func:`pyedgeconnect.EdgeConnect.get_port_forwarding_rules`
   * Retrieves existing port forwarding rules on appliance
* :func:`pyedgeconnect.EdgeConnect.set_port_forwarding_rules`
   * Updates port forwarding rules on appliance