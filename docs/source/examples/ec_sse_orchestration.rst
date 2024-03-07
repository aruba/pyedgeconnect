.. _ec_sse_quickstart:

EdgeConnect and SSE Quickstart Orchestration
**************************************************

.. note::

    The code referenced in this document and all published examples
    with pyedgeconnect are available from the GitHub repository within the
    `examples <https://github.com/aruba/pyedgeconnect/tree/main/examples>`_
    folder. Each example script contains logic to authenticate to the
    Orchestrator as documented in the authentication example.

    Clone the repository and download the examples with:

    .. code:: bash

        $ git clone https://github.com/aruba/pyedgeconnect.git

Overview and System Prerequisites
-----------------------------------

This example code is meant to assist in attaching EdgeConnect appliances
to the HPE Aruba Networking SSE service combining the workflow of
creating a Service Orchestration service in Orchestrator for desired
appliances and required configuration in the SSE portal for the
respective tunnels from the appliances.

This workflow is meant as an interim solution for
EdgeConnect customers looking to automate third-party tunnels
to HPE SSE solution prior to the automation being built-in to
Orchestrator and/or Aruba Central. This is not meant for ongoing
maintenance, but rather, simplifying initial connectivity for a large
environment avoiding manual efforts.

If you want to get right to running it, jump to
`Required Configuration To Run Demo`_

Prerequisites:

    Configuration Parameters:

        Fill out required values in config_vars.py file
            - Orchestrator name for new Service Orchestration service
            - Tunnel prefix for tunnel aliases in Orchestrator
            - FQDN for local IKE identifier for EdgeConnect appliance tunnels
            - Primary WAN labels to use for the service
            - Backup WAN labels to use for the service
            - Source interface for orchestrated IPSLA to monitor tunnels

    Authentication Parameters:

        Fill out Environment variables or rely on runtime user prompts:
            - **ORCH_URL**
              - Orchestrator FQDN or IP address (if not found will prompt inline for user input) also supported as runtime argument (-o)
            - **ORCH_API_KEY**
              - Orchestrator API KEY (if not found will prompt inline for api key, if not entered will prompt for user/password auth)
            - **SSE_WORKSPACE**
              - SSE Workspace name (if not found will prompt inline for user input) also supported as runtime argument (-ssew)
            - **SSE_USER**
              - SSE admin username (if not found will prompt inline for user input)
            - **SSE_PW**
              - SSE admin password (if not found will prompt inline for user input)

There is runtime filtering so you can associate the service to
    - all appliances
    - single appliance
    - appliances in a region

Validation will check if region or hostname specified exists
in Orchestrator and only add appliances that are currently in a
reachable state.

Can choose what or all parts of workflow to run
  #) Create new service orchestration service in Orchestrator
  #) Associate remote endpoints to existing service in Orchestrator
  #) Configure locations and tunnels in sse portal with EdgeConnect
     SDWAN data from Orchestrator.

.. note::

  The script will use the configured appliance Site name as the location
  name in the SSE service, e.g. ``EdgeConnect_<Site>``. If no Site name
  is configured it will leverage the appliance hostname. If there is no
  Site name for an HA pair of appliances it will also use the first
  appliance hostname as the location name for the pair of appliances.

If changes have been made to the SSE service (creation of new locations
and/or IPSEC tunnels) the changes will be staged as pending and must
still be committed before taking affect. The ``ec_sse_quickstart.py``
script itself will complete notifying the user if there are changes
requiring a commit, however, it will not perform the commit.

It is recommended that an admin review pending changes on the SSE
portal as there may be other changes staged by other admins or
automations.

Once reviewed, there is another script included, ``sse_commit.py`` which
can use the API to perform the commit, or the changes can be committed
in the UI itself.

Architecture Overview
===============================

**Demo Directory Structure**

.. code::

    ├── edgeconnect-sse-orchestration
        ├── ec_sse_quickstart.py
        ├── config_vars.py
        ├── sse_mgmt_auth.py
        └── sse_commit.py

.. note::

    The ``sse_mgmt_auth.py`` is imported into the main script, but
    is separated for those that would like to leverage it as a helper
    function for authenticating with the SSE Management API for other
    automation tasks.

    The ``sse_commit.py`` script is broken out to commit changes to the
    SSE platform, again allowing users to use this to tie into other
    automations and/or separate the workflow of staging changes vs.
    committing them.

System & Environment Requirements
==================================

Orchestrator & EdgeConnect
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Service Orchestration was introduced in Orchestrator 9.2 for
orchestrating tunnels to endpoints other than EdgeConnect SDWAN
appliances. This enables the ability to orchestrate tunnels at the
policy level using labels to abstract configurations at scale to
3rd party IPSEC endpoints.

.. list-table:: Supported Versions
   :header-rows: 1

   * - Orchestrator
     - EdgeConnect ECOS
   * - 9.2.0+
     - 9.1.0+


Required Configuration To Run Demo
-----------------------------------

Environment Variables
==========================

The host system can be setup with environment variables for
``SSE_WORKSPACE``, ``SSE_USER``, ``SSE_PW``, ``ORCH_URL``,
``ORCH_API_KEY``, ``TUNNEL_PSK``, and ``SSE_ADMIN_TOKEN``.

The allow for identifying the SSE workspace, an account to access
the Management API of the SSE portal, authentication to Orchestrator,
a common Tunnel Pre-Shared Key for the IPSEC tunnels between EC and the
SSE platform, and finally an admin token for commiting the changes
staged to the SSE platform.

.. note::

    Make sure that your API key for Orchestrator as well as the admin
    token for the SSE platform have correct permissions for the required
    actions.

Configuration Variables
==========================

The configuration data to leverage for the IPSEC tunnels is read from
the ``config_vars.py`` file. Fill out the values as per the example
data to match your desired use. The example values are included below.

#) ``service_name`` will be the name of the Service configured
   in Orchestrator
#) ``service_prefix`` will be the prefix used to name each
   associated tunnel
#) ``service_ike_id_fqdn`` is the fqdn value to be used in templating
   the tunnel names
#) ``primary_labels`` are the primary WAN labels used to build tunnels
   from EdgeConnect appliances to the SSE service
#) ``backup_labels`` are the backup WAN labels used to build tunnels
   from EdgeConnect appliances to the SSE service
#) ``ipsla_source`` is the label or interface name to source an IPSLA on
   the EdgeConnect through the SSE service


.. code:: python

  config_vars = {
      # Specify name of new service orchestration to add
      "service_name": "NEW HPE ANW SSE",
      # Specify prefix of new service orchestration to add for tunnel aliases
      # Minimize to 3-4 characters, maximum of 5
      # Must be globally unique across all configured services
      "service_prefix": "SSE",
      # Specify domain IKE identifier, e.g., "sse.customer.lab"
      # Full IKE id would look like "EC-1_INET1@sse.customer.lab"
      "service_ike_id_fqdn": "ssedemo.zachs.lab",
      # Specify primary WAN labels to use for service, e.g., `["INET1","INET2"]`
      # "primary_labels": ["INET1", "INET2"],
      "primary_labels": ["INETA", "INETB", "INETC"],
      # Specify backup WAN labels to use for service, e.g., `["LTE"]`
      # "backup_labels": ["LTE"],
      "backup_labels": ["LTEA"],
      # Specify source interface for ipsla, e.g., interface name `lan0`
      # or interface label `LOOPBACK`
      "ipsla_source": "LOOPBACK",
  }

Logging
=========================

The script writes to local log file located in the example directory
 ``./logging/ec-service_orch_sse.log``.

The log level can be set via runtime argument (``-l``) or environment
variable (``LOG_LEVEL``). If no level is set it will default to None.

Python Script & Orchestrator API calls
======================================

Runtime arguments
^^^^^^^^^^^^^^^^^

The python script has multiple runtime arguments defined. A user must
specify ``-af`` at a minimum to guide which appliances are targeted.
The user can then choose to include ``-cso``, ``-as``, ``-sse`` for
configuring Service Orchestration, associating the service, and/or
configuring tunnels on the SSE service respectively.

All runtime arguments are as follows:

- ``-af`` or ``--appliance_filter``
    - Type: String
    - Desc: Filter which EdgeConnect appliances are used to associate to
      Service Orchestration and/or configure SSE tunnels for, acceptable
      values are `all`, `hostname:<appliance_hostname>`, or
      `region:<region_name>`
    - **REQUIRED**
- ``-cso`` or ``--configure_service_orchestration``
    - Type: Boolean
    - Desc: Create new service orchestration service in Orchestrator per
      configuration variables in config_vars.py. As this is a Boolean
      simply including the flag triggers ``True`` and omitting it leaves
      the default of ``False``.
    - Default value: ``False``
- ``-as`` or ``--associate_service``
    - Type: Boolean
    - Desc: Associate service remote endpoints for existing service to
      appliances. As this is a Boolean simply including the flag
      triggers ``True`` and omitting it leaves the default of ``False``.
    - Default value: ``False``
- ``-sse`` or ``--configure_sse``
    - Type: Boolean
    - Desc: Configure locations and tunnels on SSE portal for existing
      service and appliances. As this is a Boolean simply including the
      flag triggers ``True`` and omitting it leaves the default of
      ``False``.
    - Default value: ``False``
- ``-o`` or ``--orch``
    - Type: String
    - Desc: Specify the Orchestrator IP or FQDN if not specified via
      environment variable or interactive input.
    - Example values: ``192.0.2.100`` or ``orchestrator.<company>.com``
    - Default value: ``None``
- ``-ssew`` or ``--sse_workspace``
    - Type: String
    - Desc: SSE Service Workspace name if not specified via
      environment variable.
    - Example values: ``myCompanyTenant``
    - Default value: ``None``
- ``-ll`` or ``--log_level``
    - Type: String
    - Desc: Specify the logging level of workflow, will not log to file
      if not specified. E.g., INFO, WARNING, ERROR, etc.
    - Example values: ``INFO``, ``WARNING``, or ``ERROR``
    - Default value: ``None``

Once you've filled out the required details in your ``config_vars.py``
file as well as configured respective environment variables on the host
system the following commands will perform their respective
configuration work.

Running the script to configure a new service, associate all appliances,
and configure respective locations/tunnels on the SSE service.

.. code-block:: bash

    python ec_sse_quickstart.py -af all -cso -as -sse

Running the script to associate a single appliance to an existing
service and configure respective locations/tunnels on the SSE service.

.. code-block:: bash

    python ec_sse_quickstart.py -af hostname:My-Appliance-01 -as -sse

Running the script to configure respective locations/tunnels on the SSE
service for all appliances of an existing service.

.. code-block:: bash

    python ec_sse_quickstart.py -af all -sse


To automate commit on the SSE platform (This leverages the SSE admin
token)

.. code-block:: bash

    python sse_commit.py

Orchestrator API calls
^^^^^^^^^^^^^^^^^^^^^^^^^^

The three API calls to Orchestrator (outside of authentication) are:

- :func:`pyedgeconnect.Orchestrator.get_appliances`
   - gets inventory of all appliances in Orchestrator
- :func:`pyedgeconnect.Orchestrator.get_interface_labels_by_type`
   - gets all configured interface labels
- :func:`pyedgeconnect.Orchestrator.get_service_orchestration_all_names_to_ids`
   - gets id values of configured Service Orchestration services
- :func:`pyedgeconnect.Orchestrator.add_new_service_orchestration`
   - creates a new service in Service Orchestration
- :func:`pyedgeconnect.Orchestrator.set_service_orchestration_labels`
   - sets WAN labels to use for a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.set_service_orchestration_tunnel_settings`
   - sets tunnel settings to use for a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.get_service_orchestration_remote_endpoints`
   - gets configured remote endpoints for a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.add_service_orchestration_remote_endpoints`
   - configures remote endpoints for a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.get_service_orchestration_appliance_association`
   - gets appliance association for a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.set_service_orchestration_appliance_association`
   - associates appliances to a Service Orchestration service
- :func:`pyedgeconnect.Orchestrator.get_all_appliance_deployment`
   - gets all deployment information for all appliances
- :func:`pyedgeconnect.Orchestrator.get_ha_groups`
   - gets all EdgeHA pairs of appliances

SSE Management API calls
^^^^^^^^^^^^^^^^^^^^^^^^^^

- GET /Location
   - Gets existing Locations configured in SSE service
- GET /Tunnel
   - Gets existing IPSEC Tunnels configured in SSE service
- POST /Location
   - Creates new Location in SSE service
- POST /Tunnel
   - Creates new IPSEC Tunnel in SSE service