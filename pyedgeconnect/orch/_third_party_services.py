# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# thirdPartyServices : Third Party Services Orchestration
from __future__ import annotations

# ZScaler - todo
# Check Point - todo
# Azure - todo
# AWS - todo


# Aruba Clearpass
def clearpass_get_configured_accounts(
    self,
) -> dict:
    """Get all ClearPass accounts with ID

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/accounts

    :return: Returns dictionary of configured ClearPass Policy Manager
      accounts \n
        * keyword **<account_id>** (`dict`): CPPM account object id \n
            * keyword **name** (`str`): Configured name of CPPM in
              Orchestrator
            * keyword **domain** (`str`): IP or FQDN of CPPM
            * keyword **clientId** (`str`): Account ID to access CPPM
            * keyword **verifyCert** (`bool`): If Orchestrator is set to
              validate certificate of CPPM server
    :rtype: dict
    """
    return self._get("/thirdPartyServices/clearpass/accounts")


def clearpass_add_account(
    self,
    name: str,
    domain: str,
    client_id: str,
    access_key: str,
    verify_cert: bool,
) -> str:
    """Add new ClearPass Policy Manager account to Orchestrator

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/clearpass/accounts

    :param name: Name to identify CPPM in UI, must be a unique value
    :type name: str
    :param domain: IP address or FQDN of CPPM server to connect, must be
        a unique value
    :type domain: str
    :param client_id: Client ID to connect to CPPM with
    :type client_id: str
    :param access_key: Access key to authenticate connection to CPPM
    :type access_key: str
    :param verify_cert: ``True`` to have Orchestrator verify CPPM
        certificate, ``False`` to not verify
    :type verify_cert: bool
    :return: Returns empty response on success or error details of a
        failed attempt to add CPPM account
    :rtype: str
    """
    data = {
        "name": name,
        "domain": domain,
        "clientId": client_id,
        "accessKey": access_key,
        "verifyCert": verify_cert,
    }

    return self._post(
        "/thirdPartyServices/clearpass/accounts",
        data=data,
        expected_status=[204],
        return_type="text",
    )


def clearpass_get_configured_account(
    self,
    account_id: int,
) -> dict:
    """Get ClearPass Policy Manager account details using ID

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/accounts/{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns dictionary of configured ClearPass Policy Manager
      account \n
        * keyword **name** (`str`): Configured name of CPPM in
          Orchestrator
        * keyword **domain** (`str`): IP or FQDN of CPPM
        * keyword **clientId** (`str`): Account ID to access CPPM
        * keyword **verifyCert** (`bool`): If Orchestrator is set to
          validate certificate of CPPM server
    :rtype: dict
    """
    return self._get(f"/thirdPartyServices/clearpass/accounts/{account_id}")


def clearpass_update_account(
    self,
    name: str,
    domain: str,
    client_id: str,
    access_key: str,
    verify_cert: bool,
    account_id: int,
) -> str:
    """Update ClearPass Policy Manager account configuration.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - PUT
          - /thirdPartyServices/clearpass/accounts{id}

    :param name: Name to identify CPPM in UI, must be a unique value
    :type name: str
    :param domain: IP address or FQDN of CPPM server to connect, must be
        a unique value
    :type domain: str
    :param client_id: Client ID to connect to CPPM with
    :type client_id: str
    :param access_key: Access key to authenticate connection to CPPM
    :type access_key: str
    :param verify_cert: ``True`` to have Orchestrator verify CPPM
        certificate, ``False`` to not verify
    :type verify_cert: bool
    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns empty response on success or error details of a
        failed attempt to add CPPM account
    :rtype: str
    """
    data = {
        "name": name,
        "domain": domain,
        "clientId": client_id,
        "accessKey": access_key,
        "verifyCert": verify_cert,
    }

    return self._put(
        f"/thirdPartyServices/clearpass/accounts/{account_id}",
        data=data,
        expected_status=[204],
        return_type="text",
    )


def clearpass_delete_account(
    self,
    account_id: int,
) -> str:
    """Delete ClearPass Policy Manager account configuration.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - DELETE
          - /thirdPartyServices/clearpass/accounts{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns empty 204 response on success or error details of a
        failed attempt to add CPPM account
    :rtype: str
    """

    return self._delete(
        f"/thirdPartyServices/clearpass/accounts/{account_id}",
        expected_status=[204],
        return_type="text",
    )


def clearpass_get_configured_account_details(
    self,
    account_id: int,
) -> dict:
    """Get all ClearPass Policy Manager configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/configurations/{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns dictionary of configured ClearPass Policy Manager
      account configuration\n
        * keyword **id** (`int`): Account ID,
        * keyword **name** (`str`): Unique user defined name for the
          clearpass configuration
        * keyword **domain** (`str`): Azure VPN Site ID to which VPN
          Connection is established.
        * keyword **configData** (`str`): ClearPass Account details in a
          string-formatted dictionary
        * keyword **serviceInfo** (`str`): ClearPass service endpoint
          information in a string-formatted dictionary
        * keyword **status** (`int`): ClearPass account connection
          status, ``0`` disconnected, ``1`` connected
        * keyword **serviceStatus** (`int`): Not documented in Swagger
          , ``0`` disconnected, ``1`` connected
        * keyword **paused** (`bool`): Account pause status, ``True`` if
          paused, ``False`` if active
        * keyword **needService** (`bool`): boolean value to decide
          whether the account needs service, ``True`` if needs service,
          ``False`` if no service required
    :rtype: dict
    """
    return self._get(
        f"/thirdPartyServices/clearpass/configurations/{account_id}"
    )  # noqa: E501


def clearpass_pause_individual_orchestration(
    self,
    pause: bool,
    account_id: int,
) -> str:
    """Pause individual ClearPass Policy Manager orchestration.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - PUT
          - /thirdPartyServices/clearpass/accounts/pause/{id}

    :param pause: Set pause status of Orchestration with CPPM, ``True``
        to pause, ``False`` to make active
    :type pause: bool
    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns ``1`` on successful call, otherwise provides error
        message if invalid ID
    :rtype: str
    """

    return self._put(
        f"/thirdPartyServices/clearpass/accounts/pause/{account_id}?isPaused={pause}",  # noqa: E501
        return_type="text",
    )


def clearpass_get_pause_orchestration_status(
    self,
) -> dict:
    """Get ClearPass Policy Manager pause orchestration status.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/pauseOrchestration

    :return: Returns dictionary of ClearPass Policy Manager
      Orchestration pause status \n
        * keyword **paused** (`bool`): ``True`` if paused, ``False`` if
          active
    :rtype: dict
    """
    return self._get("/thirdPartyServices/clearpass/pauseOrchestration")


def clearpass_set_pause_orchestration_status(
    self,
    pause: bool,
) -> bool:
    """Set ClearPass Policy Manager pause orchestration status.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/clearpass/pauseOrchestration

    :param pause: ``True`` to pause orchestration, ``False`` to resume
    :type pause: bool
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    data = {"paused": pause}
    return self._post(
        "/thirdPartyServices/clearpass/pauseOrchestration",
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def clearpass_get_service_endpoint_status(
    self,
    account_id: int,
) -> dict:
    """Get ClearPass Policy Manager service endpoint status.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/service/status/{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns dictionary of ClearPass Policy Manager service
      status \n
        * keyword **context_server** (`int`): ``1`` if active, ``0`` if
          failed
        * keyword **login_context_server_action** (`int`): ``1`` if
          active, ``0`` if failed
        * keyword **logout_context_server_action** (`int`): ``1`` if
          active, ``0`` if failed
    :rtype: dict
    """
    return self._get(
        f"/thirdPartyServices/clearpass/service/status/{account_id}"
    )  # noqa: E501


def clearpass_reset_service_endpoint(
    self,
    account_id: int,
    service: str,
) -> dict:
    """Reset ClearPass Policy Manager service endpoint.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - PUT
          - /thirdPartyServices/clearpass/service/status/{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :param service: Service to reset, accepted values are
      ``context_server``, ``login_context_server_action``, and
      ``logout_context_server_action``
    :type service: str
    :return: Returns dictionary of ClearPass Policy Manager service
      status \n
        * keyword **context_server** (`int`): ``1`` if active, ``0`` if
          failed
        * keyword **login_context_server_action** (`int`): ``1`` if
          active, ``0`` if failed
        * keyword **logout_context_server_action** (`int`): ``1`` if
          active, ``0`` if failed
    :rtype: dict
    """
    return self._put(
        f"/thirdPartyServices/clearpass/service/status/{account_id}?service={service}"  # noqa: W505
    )


def clearpass_get_connectivity(
    self,
    account_id: int,
) -> dict:
    """Get ClearPass Policy Manager account connectivity status

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/connectivity/{id}

    :param account_id: Integer ID of configured CPPM account
    :type account_id: int
    :return: Returns dictionary of ClearPass Policy Manager connectivity
      status \n
        * keyword **connectivity** (`str`): The connectivity status to
          ClearPass Policy Manager: ``0`` - Not Connected, ``1`` -
          Connected, ``2`` - Auth Failed, ``3``- Unreachable
    :rtype: dict
    """
    return self._get(
        f"/thirdPartyServices/clearpass/connectivity/{account_id}"
    )  # noqa: E501


def clearpass_post_login_event(
    self,
    timestamp: str = "",
    event_type: str = "",
    ip_address: str = "",
    cppm_domain: str = "",
    username: str = "",
    device_os: str = "",
    roles: str = "",
    ssid: str = "",
    auth_protocol: str = "",
    posture: str = "",
    mac: str = "",
    location_id: str = "",
    other_info: str = "",
) -> bool:
    """Posts ClearPass Policy Manager login event

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/clearpass/event/login

    :param timestamp: ClearPass policy manager event timestamp.
      Timestamp format : yyyy-MM-dd HH:mm:ss
    :type timestamp: str
    :param event_type: Event type (login/logout)
    :type event_type: str
    :param ip_address: Client's IP address
    :type ip_address: str
    :param cppm_domain: ClearPass Policy Manager's domain IP
    :type cppm_domain: str
    :param username: client's username
    :type username: str
    :param device_os: Identified device OS
    :type device_os: str
    :param roles: User roles
    :type roles: str
    :param ssid: Device's SSID
    :type ssid: str
    :param auth_protocol: Authentication protocol type
    :type auth_protocol: str
    :param posture: device health info
    :type posture: str
    :param mac: Client's mac address
    :type mac: str
    :param location_id: Access point's location ID
    :type location_id: str
    :param other_info: Unmatched extra info in JSON format
    :type other_info: str
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    data = {
        "timestamp": timestamp,
        "eventType": event_type,
        "ipAddress": ip_address,
        "cppmDomain": cppm_domain,
        "username": username,
        "deviceOS": device_os,
        "roles": roles,
        "ssid": ssid,
        "authProtocol": auth_protocol,
        "posture": posture,
        "mac": mac,
        "locationId": location_id,
        "otherInfo": other_info,
    }

    return self._post(
        "/thirdPartyServices/clearpass/event/login",
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def clearpass_post_logout_event(
    self,
    timestamp: str = "",
    event_type: str = "",
    ip_address: str = "",
    cppm_domain: str = "",
    username: str = "",
    device_os: str = "",
    roles: str = "",
    ssid: str = "",
    auth_protocol: str = "",
    posture: str = "",
    mac: str = "",
    location_id: str = "",
    other_info: str = "",
) -> bool:
    """Posts ClearPass Policy Manager logout event

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/clearpass/event/logout

    :param timestamp: ClearPass policy manager event timestamp
    :type timestamp: str
    :param event_type: Event type (login/logout)
    :type event_type: str
    :param ip_address: Client's IP address
    :type ip_address: str
    :param cppm_domain: ClearPass Policy Manager's domain IP
    :type cppm_domain: str
    :param username: client's username
    :type username: str
    :param device_os: Identified device OS
    :type device_os: str
    :param roles: User roles
    :type roles: str
    :param ssid: Device's SSID
    :type ssid: str
    :param auth_protocol: Authentication protocol type
    :type auth_protocol: str
    :param posture: device health info
    :type posture: str
    :param mac: Client's mac address
    :type mac: str
    :param location_id: Access point's location ID
    :type location_id: str
    :param other_info: Unmatched extra info in JSON format
    :type other_info: str
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    data = {
        "timestamp": timestamp,
        "eventType": event_type,
        "ipAddress": ip_address,
        "cppmDomain": cppm_domain,
        "username": username,
        "deviceOS": device_os,
        "roles": roles,
        "ssid": ssid,
        "authProtocol": auth_protocol,
        "posture": posture,
        "mac": mac,
        "locationId": location_id,
        "otherInfo": other_info,
    }

    return self._post(
        "/thirdPartyServices/clearpass/event/logout",
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def clearpass_filter_events(
    self,
    start_time: int,
    end_time: int,
    ip_address: str = None,
    username: str = None,
    limit: int = 10000,
    event_type: str = None,
) -> list:
    """Filter ClearPass Policy Manager events

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/events/filter

    :param start_time: Long(Signed 64 bits) value of milliseconds since
      EPOCH time indicating the starting time boundary of data time
      range
    :type start_time: int
    :param end_time: Long(Signed 64 bits) value of milliseconds since
      EPOCH time indicating the ending time boundary of data time range
    :type end_time: int
    :param ip_address: IP address to filter for, e.g. ``10.1.1.100``,
      defaults to None
    :type ip_address: str, optional
    :param username: Username to filter for, defaults to None
    :type username: str, optional
    :param limit: Limit number of returned results, defaults to
      ``10000``
    :type limit: int, optional
    :param event_type: Event filter type. Please specify one of these
      values ``All``, ``Active``, ``Historical``, defaults to None
    :type event_type: str, optional
    :return: Returns list of ClearPass Policy Manager events \n
        [`dict`]: ClearPass event object \n
            * keyword **timestamp** (`str`): ClearPass policy manager
              event timestamp
            * keyword **eventType** (`str`): Event type (login/logout)
            * keyword **ipAddress** (`str`): Client's IP address
            * keyword **cppmDomain** (`str`): ClearPass Policy Manager's
              domain IP
            * keyword **username** (`str`): client's username
            * keyword **deviceOS** (`str`): Identified device OS
            * keyword **roles** (`str`): User roles
            * keyword **ssid** (`str`): Device's SSID
            * keyword **authProtocol** (`str`): Authentication protocol
              type
            * keyword **posture** (`str`): device health info
            * keyword **mac** (`str`): Client's mac address
            * keyword **locationId** (`str`): Access point's location ID
            * keyword **otherInfo** (`str`): Unmatched extra info in
              JSON format
    :rtype: list
    """
    path = f"/thirdPartyServices/clearpass/events/filter?startTime={start_time}&endTime={end_time}"  # noqa: E501

    if ip_address is not None:
        path += f"&ip={ip_address}"
    if username is not None:
        path += f"&username={username}"

    path += f"&limit={limit}"

    if event_type is not None:
        path += f"&type={event_type}"

    return self._get(path)


def clearpass_get_user_roles_for_ip(
    self,
    ip_address: str,
    start_time: int = None,
    end_time: int = None,
) -> dict:
    """Get username and role list for given IP and time range

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/clearpass/events/filter/userinfo/{ip}

    :param ip_address: IP address to filter for, e.g. ``10.1.1.100``
    :type ip_address: str
    :param start_time: Long(Signed 64 bits) value of milliseconds since
      EPOCH time indicating the starting time boundary of data time
      range, defaults to None
    :type start_time: int, optional
    :param end_time: Long(Signed 64 bits) value of milliseconds since
      EPOCH time indicating the ending time boundary of data time range,
      defaults to None
    :type end_time: int, optional
    :return: Returns dictionary of usernames and roles matching a given
      IP address within the specified time range \n
        * keyword **roles** (`list[str]`): list of roles
        * keyword **usernames** (`list[str]`): list of usernames
    :rtype: dict
    """
    path = f"/thirdPartyServices/clearpass/events/filter/userinfo/{ip_address}"

    if start_time is not None:
        path += f"&startTime={start_time}"
    if end_time is not None:
        path += f"&endTime={end_time}"

    return self._get(path)


# Aruba Central
def central_get_subscription(
    self,
) -> dict:
    """Returns Aruba Central subscription

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/arubaCentral/subscription

    :return: Returns dictionary of aruba central subscription
      information \n
        * keyword **customerId** (`str`): The Customer ID of Aruba
          Central
        * keyword **username** (`str`): The username of Aruba Central
        * keyword **password** (`str`, optional): The password of Aruba
          Central
        * keyword **clientId** (`str`): clientId to use for Orchestrator
          mapping
        * keyword **clientSecret** (`str`): clientSecret to use for
          Orchestrator mapping
        * keyword **domain** (`str`): Domain to use for Orchestrator
          mapping
    :rtype: dict
    """
    return self._get("/thirdPartyServices/arubaCentral/subscription")


def central_add_subscription(
    self,
    customer_id: str,
    username: str,
    password: str,
    client_id: str,
    client_secret: str,
    domain: str,
) -> bool:
    """Add/Update Aruba Central subscription

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/arubaCentral/subscription

    :param customer_id: The Customer ID of Aruba Central
    :type customer_id: str
    :param username: The username of Aruba Central
    :type username: str
    :param password: The password of Aruba Central
    :type password: str
    :param client_id: clientId to use for Orchestrator mapping
    :type client_id: str
    :param client_secret: clientSecret to use for Orchestrator mapping
    :type client_secret: str
    :param domain: Domain to use for Orchestrator
    :type domain: str
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    data = {
        "customerId": customer_id,
        "username": username,
        "password": password,
        "clientId": client_id,
        "clientSecret": client_secret,
        "domain": domain,
    }

    return self._post(
        "/thirdPartyServices/arubaCentral/subscription",
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def central_delete_subscription(
    self,
) -> bool:
    """Delete Aruba Central subscription

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - DELETE
          - /thirdPartyServices/arubaCentral/subscription

    :return: Returns True/False based on successful call
    :rtype: bool
    """

    return self._delete(
        "/thirdPartyServices/arubaCentral/subscription",
        expected_status=[204],
        return_type="bool",
    )


def central_get_site_mapping(
    self,
) -> list:
    """Get Aruba Central site and appliances mapping

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/arubaCentral/sitesMapping

    :return: Returns list of dictionaries with site mapping
      to Edge Connect appliance relationships \n
        * [`dict`]: List of site to appliance relationship objects \n
          * keyword <site_id_#> (`list[dict]`): Key is Site ID string
            integer, list of appliance object dictionaries related to
            site \n
            * keyword **nePk** (`str`): Appliance ID
            * keyword **applianceName** (`str`): Appliance hostname
            * keyword **recommendSite** (`str`): Recommended site ID
            * keyword **gmsMarked** (`bool`): ``True`` if set by
              Orchestrator
    :rtype: List
    """

    return self._get("/thirdPartyServices/arubaCentral/sitesMapping")


def central_assign_appliance_to_site(
    self,
    ne_pk: str,
    origin_site: str = None,
    new_site: str = None,
) -> bool:
    """Manually assign appliance to the aruba central site

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/arubaCentral/sitesMapping/{nePk}


    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param origin_site: Aruba Central site ID appliance originally
      associated to, defaults to None
    :type origin_site: str, optional
    :param new_site: New Aruba Central site ID to associate appliance
      to, defaults to None
    :type new_site: str, optional
    :return: Returns True/False based on successful call
    :rtype: bool
    """
    data = {
        "origin": origin_site,
        "siteId": new_site,
    }
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/arubaCentral/sitesMapping?nePk={ne_pk}"
    else:
        path = f"/thirdPartyServices/arubaCentral/sitesMapping/{ne_pk}"

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def get_service_orchestration_breakout_state(
    self,
    service_id: str,
) -> dict:
    """Get a Service Orchestration Breakout state, if set to ``1``
    service is available in BIO Breakout Internet Policies for
    an overlay.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/bioBreakout/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns dictionary of particular service BIO breakout state\n
        * keyword **bioBreakout** (`int`): ``1`` service added to BIO
          breakout internet policies, ``0`` means removed from breakout
          list
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/bioBreakout?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/bioBreakout/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_breakout_state(
    self,
    service_id: str,
    breakout_state: int,
) -> bool:
    """Set a Service Orchestration Breakout state, if set to `1` service
    is available in BIO Breakout Internet Policies for an overlay.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/bioBreakout/{serviceId}


    :param service_id: String integer id of the service to query
    :type service_id: str
    :param breakout_state: `1` for available for breakout, `0` for not
    :type breakout_state: int
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {"bioBreakout": breakout_state}

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/bioBreakout?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/bioBreakout/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def get_service_orchestration_labels(
    self,
    service_id: str,
) -> list[list[str], list[str]]:
    """Get a Service Orchestration label association, returns list of
    lists. First nested list is labels for primary tunnels and second
    list is labels for backup tunnels. e.g. ``[["2","5"],["3"]]`` where
    "2" and "5" are primary labels and "3" is a backup label.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/interfaces/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns list of lists. First nested list is label
      ids for primary tunnels and second list is labels for backup
      tunnels.
    :rtype: list[list[str],list[str]]
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/interfaces?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/interfaces/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_labels(
    self,
    service_id: str,
    labels: list[list[str], list[str]],
) -> bool:
    """Set a Service Orchestration label association for primary
    and backup tunnels for a serivce. First nested list is labels for
    primary tunnels and second list is labels for backup tunnels. e.g.
    ``[["2","5"],["3"]]`` where ``2`` and ``5`` are primary labels and
    ``3`` is a backup label. You can use
    :func:`~pyedgeconnect.Orchestrator.get_interface_labels_by_type`
    with parameters ``label_type`` set to ``wan`` and ``active`` set to
    ``True`` to pull the active WAN labels and find their respective
    id values.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/interfaces/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param labels: First nested list is labels for primary tunnels and
      second list is labels for backup tunnels. e.g.
      ``[["2","5"],["3"]]`` where ``2`` and ``5`` are primary labels and
      ``3`` is a backup label.
    :type labels: list[list[str],list[str]]
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {"ids": labels}

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/interfaces?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/interfaces/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def get_service_orchestration_all_names_to_ids(
    self,
) -> dict:
    """Get Service Orchestration names to id mappings.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/serviceIdToName

    :return: Returns dictionary of service orchestration ids to friendly
      name mappings \n
      * keyword **<service_id>** (`str`): Service name
    :rtype: dict
    """
    return self._get(
        "/thirdPartyServices/serviceOrchestration/serviceIdToName",
    )


def get_service_orchestration_all_services(
    self,
) -> list[dict]:
    """Get Service Orchestration names to id mappings.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/serviceProviders

    :return: Returns list of dictionaries of each service configured by
      Service Orchestration and respective details \n
      * [`dict`]: Service Orchestration object \n
        * keyword **serviceId** (`int`): Service id
        * keyword **servicePrefix** (`str`): Service prefix (e.g. `NSK`)
          which will be used as a prefix in the alias of associated
          tunnels
        * keyword **serviceIcon** (`str`): Icon in text format
        * keyword **serviceIconPath** (`str`): Path to icon image
        * keyword **bioBreakout** (`int`): `1` if service is configured
          as available for internet breakout policy
        * keyword **pauseOrchestration** (`int`): `1` if service is
          paused from Orchestration
        * keyword **interfaces** (`str`): Escaped string list of primary
          and backup labels for tunnels
        * keyword **tunnelSettings** (`str`): Escaped string dictionary
          of Tunnel configuration settings for the service
        * keyword **ipslaSettings** (`str`): Escaped string dictionary
          of IPSLA configuration settings for the service
        * keyword **timestamp** (`int`): timestamp
    :rtype: dict
    """
    return self._get(
        "/thirdPartyServices/serviceOrchestration/serviceProviders",
    )


def add_new_service_orchestration(
    self,
    service_name: str,
    service_prefix: str,
    bio_breakout: int,
    pause_orchestration: int = None,
) -> dict:
    """Create new Service Orchestration service

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/serviceProviders
    :param service_name: Name of the service
    :type service_name: str
    :param service_prefix: Prefix for tunnel aliases of related service
    :type service_prefix: str
    :param bio_breakout: `1` for making service available as Internet
      Breakout policy
    :type bio_breakout: int
    :param pause_orchestration: `1` to pause Orchestration for this
      service, `0` to not. Defaults to None
    :type pause_orchestration: int, optional
    :return: Returns dictionary of newly configured service \n
      * keyword **serviceId** (`int`): Service id
      * keyword **servicePrefix** (`str`): Service prefix (e.g. `NSK`)
        which will be used as a prefix in the alias of associated
        tunnels
      * keyword **serviceIcon** (`str`): Icon in text format
      * keyword **serviceIconPath** (`str`): Path to icon image
      * keyword **bioBreakout** (`int`): `1` if service is configured
        as available for internet breakout policy
      * keyword **pauseOrchestration** (`int`): `1` if service is
        paused from Orchestration
      * keyword **interfaces** (`str`): Escaped string list of primary
        and backup labels for tunnels
      * keyword **tunnelSettings** (`str`): Escaped string dictionary
        of Tunnel configuration settings for the service
      * keyword **ipslaSettings** (`str`): Escaped string dictionary
        of IPSLA configuration settings for the service
      * keyword **timestamp** (`int`): timestamp
    :rtype: dict
    """
    data = {
        "serviceName": service_name,
        "servicePrefix": service_prefix,
        "bioBreakout": bio_breakout,
    }

    if pause_orchestration is not None:
        data["pauseOrchestration"] = pause_orchestration

    return self._post(
        "/thirdPartyServices/serviceOrchestration/serviceProviders",
        data=data,
    )


def delete_service_orchestration(
    self,
    service_id: str,
) -> bool:
    """Delete Service Orchestration service

    .. warning::
      Unlike in the Web UI, this function will immediately delete
      a configured service for Service Orchestration. That will remove
      all configuration of the service, assocation to any appliances,
      and thus remove the service from Overlay policy and any tunnels
      that appliances may have for this service. You have to be
      completely sure to validate the level of impact if you are
      deleting a service from Service Orchesration that may be in use.

    .. note::
      This API Call is not in current Swagger as of Orch 9.3.1

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - DELETE
          - /thirdPartyServices/serviceOrchestration/serviceProvider/{serviceId}

    :param service_id: String integer id of the service to delete
    :type service_id: str
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/serviceProvider?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/serviceProvider/{service_id}"  # noqa: E501

    return self._delete(
        path,
        return_type="bool",
    )


def get_service_orchestration_tunnel_settings(
    self,
    service_id: str,
) -> dict:
    """Get Service Orchestration tunnel settings for particular service

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/tunnelSetting/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns dictionary of tunnel settings for service \n
      * keyword **admin** (`str`): Admin ``up`` or ``down`` for tunnel
      * keyword **mode** (`str`): Passthrough tunnel mode, ``ipsec_ip``
      * keyword **autoMaxBandwidthEnabled** (`bool`): ``True`` for
        determining maximum bandwidth for tunnel automatically
      * keyword **ipSecSuiteB** (`str`): IPSec Suite B parameters
        e.g., ``GCM-128``, ``GMAC-256``, etc.
      * keyword **presharedKey** (`str`): Pre-shared Key will return
        as blank string for security reasons
      * keyword **ikeAuthenticationAlgorithm** (`str`): IKE
        authentication algorithim, e.g., ``sha1``
      * keyword **ikeEncryptionAlgorithm** (`str`): IKE
        authentication algorithim, e.g., ``aes128``
      * keyword **ikePrf** (`str`): auto
      * keyword **dhgroup** (`int`): Diffe-Hellman group number,
        e.g., ``14``
      * keyword **ikeLifetime** (`int`): IKE lifetime in minutes,
        e.g., ``480``
      * keyword **dpdDelay** (`int`): Dead Peer Detection delay value
        in seconds, generally 3x the value of retry value e.g. ``10``
      * keyword **dpdRetry** (`int`): Dead Peer Detection retry value
        in seconds, e.g. ``3``
      * keyword **idType** (`str`): IKE identifier type used, defaults
        to ``address``
      * keyword **idStr** (`str`): Returns as blank string as it is
        dynamically set per appliance and label
      * keyword **exchangeMode** (`str`): Exchange mode,
        e.g., ``aggressive``
      * keyword **ikeVersion** (`int`): IKE version ``1`` or ``2``
      * keyword **ikeIdFormat** (`str`): Format for tunnel IKE
        identifier, can use dynamic variables from appliance,
        e.g., ``%hostname%_%label%@%tunnel_dst%``
      * keyword **authenticationAlgorithm** (`str`): Authentication
        algorithm, e.g., ``sha1``
      * keyword **encryptionAlgorithm** (`str`): Encryption
        algorithm, e.g., ``aes128``
      * keyword **ipsecAntiReplayWindow** (`str`): ``enable`` or
        ``disable`` ipsec anti-replay window setting. Defaults to
        ``disable``.
      * keyword **lifebytes** (`int`): IPSEC Lifetime megabytes
      * keyword **lifetime** (`int`): IPSEC Lifetime in minutes
      * keyword **pfs** (`bool`): ``True`` for perfect forward secrecy
      * keyword **pfsgroup** (`str`): Perfect forward secrecy group
        number
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelSetting?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelSetting/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_tunnel_settings(
    self,
    service_id: str,
    admin: str = "up",
    mode: str = "ipsec_ip",
    auto_max_bw_enabled: bool = True,
    ipsec_suite_b: str = None,
    ike_auth_algo: str = "sha1",
    ike_encrypt_algo: str = "aes128",
    ikePrf: str = "auto",
    dhgroup: int = 14,
    ike_lifetime: int = 480,
    dpd_delay: int = 10,
    dpd_retry: int = 3,
    id_type: str = "address",
    exchange_mode: str = "aggressive",
    ike_version: int = 2,
    ike_id_format: str = r"%hostname%_%label%@%tunnel_dst%",
    auth_algo: str = "sha1",
    encrypt_algo: str = "aes128",
    ipsec_anti_replay_window: str = "disable",
    lifebytes: int = 0,
    lifetime: int = 120,
    pfs: bool = True,
    pfsgroup: str = "14",
) -> bool:
    """Set Service Orchestration service tunnel settings. Default values
    are default values from Orchestrator when creating a new service.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/tunnelSetting/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param admin: Admin state of tunnel, defaults to ``up``
    :type admin: str, optional
    :param mode: Passthrough tunnel mode, defaults to ``ipsec_ip``
    :type mode: str = "ipsec_ip", optional
    :param auto_max_bw_enabled: Auto-max bandwidth enabled for tunnel
      based on bandwidth of interface that tunnel is being made on,
      defaults to ``True``
    :type auto_max_bw_enabled: bool, optional
    :param ipsec_suite_b: IPSec Suite B presets, defaults to ``None``
    :type ipsec_suite_b: str, optional
    :param ike_auth_algo: IKE uthentication algorithm, defaults to
      ``sha1``
    :type ike_auth_algo: str, optional
    :param ike_encrypt_algo: IKE encryption algorithm, defaults to
      ``aes128``
    :type ike_encrypt_algo: str, optional
    :param ikePrf: defaults to ``auto``
    :type ikePrf: str, optional
    :param dhgroup: Diffie Hellman group number, defaults to ``14``
    :type dhgroup: int, optional
    :param ike_lifetime: IKE rekey/lifetime timer setting in minutes,
      defaults to 480
    :type ike_lifetime: int, optional
    :param dpd_delay: Dead Peer Detection delay timer in seconds,
      defaults to 10
    :type dpd_delay: int, optional
    :param dpd_retry: Dead Peer Detection retry timer in seconds,
      defaults to 3
    :type dpd_retry: int, optional
    :param id_type: IKE ID type, defaults to ``address``
    :type id_type: str, optional
    :param exchange_mode: IKE exchange mode, defaults to ``aggressive``
    :type exchange_mode: str, optional
    :param ike_version: IKE version, defaults to ``2``
    :type ike_version: int, optional
    :param ike_id_format: Local IKE ID format, allowing variable-based
      ID's based on values such as appliance hostname, label, etc.
      Defaults to string that UI defaults to in Orchestrator of
      ``%hostname%_%label%@%tunnel_dst%``
    :type ike_id_format: str, optional
    :param auth_algo: IPSec authentication algorithm, defaults to
      ``sha1``
    :type auth_algo: str, optional
    :param encrypt_algo: IPSec encryption algorithm, defaults to
      ``aes128``
    :type encrypt_algo: str, optional
    :param ipsec_anti_replay_window: Enable anti-replay window in number
      of packets. Acceptable values are ``disable`` to disable, or
      number of packets either ``1024``, ``8192``, or ``65536``,
      defaults to ``disable``
    :type ipsec_anti_replay_window: str, optional
    :param lifebytes: Anti-replay lifetime in units of bytes, ``0``
      will be treated as disabled, defaults to ``0``
    :type lifebytes: int = 0, optional
    :param lifetime: Anti-replay lifetime in units of minutes, ``0``
      will be treated as disabled, defaults to ``120``
    :type lifetime: int, optional
    :param pfs: Enable Perfect Forward Secrecy, defaults to ``True``
    :type pfs: bool, optional
    :param pfsgroup: Perfect Forward Secrecy group, defaults to ``14``
    :type pfsgroup: str, optional
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {
        "admin": admin,
        "mode": mode,
        "autoMaxBandwidthEnabled": auto_max_bw_enabled,
        "ipSecSuiteB": ipsec_suite_b,
        "ikeAuthenticationAlgorithm": ike_auth_algo,
        "ikeEncryptionAlgorithm": ike_encrypt_algo,
        "ikePrf": ikePrf,
        "dhgroup": dhgroup,
        "ikeLifetime": ike_lifetime,
        "dpdDelay": dpd_delay,
        "dpdRetry": dpd_retry,
        "idType": id_type,
        "exchangeMode": exchange_mode,
        "ikeVersion": ike_version,
        "ikeIdFormat": ike_id_format,
        "authenticationAlgorithm": auth_algo,
        "encryptionAlgorithm": encrypt_algo,
        "ipsecAntiReplayWindow": ipsec_anti_replay_window,
        "lifebytes": lifebytes,
        "lifetime": lifetime,
        "pfs": pfs,
        "pfsgroup": pfsgroup,
    }

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelSetting?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelSetting/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        return_type="bool",
    )


def get_service_orchestration_tunnel_identifiers(
    self,
    service_id: str,
) -> dict:
    """Get Service Orchestration tunnel identifiers for particular
    service

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/tunnelIdentifiers/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns dictionary of tunnel identifiers for service \n
      * keyword **<nepk_labelId_remoteEndpointId>** (`dict`): Tunnel
        identifer object \n
        * keyword **localIkeIdentifier** (`str`): Local IKE identifer
        * keyword **primaryRemoteIkeIdentifier** (`str`): Primary
          remote IKE identifer
        * keyword **backupRemoteIkeIdentifier** (`str`): Backup
          remote IKE identifer
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelIdentifiers?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/tunnelIdentifiers/{service_id}"  # noqa: E501

    return self._get(path)


def get_service_orchestration_config_entries(
    self,
    service_id: str,
) -> dict:
    """Get Service Orchestration configuration entries for particular
    service

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/serviceConfigurationEntries/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns dictionary of configuration entries for service \n
      * keyword **service_id** (`int`): Service ID number
      * keyword **remoteEndpointId** (`int`): Primary remote endpoint id
      * keyword **backupEndpointId** (`str`): Backup remote endpoint id
      * keyword **nepk** (`str`): Appliance NEPK id value
      * keyword **labelId** (`str`): WAN Label ID
      * keyword **labelType** (`str`): WAN Label type for service
        ``Primary`` or ``Backup``
      * keyword **remoteEndpointName** (`str`): Primary remote endpoint
        friendly name
      * keyword **backupEndpointName** (`str`): Backup remote endpoint
        friendly name
      * keyword **tunnelStatus** (`str`): Tunnel status, e.g., ``Up``
      * keyword **timestamp** (`int`): Timestamp
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/serviceConfigurationEntries?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/serviceConfigurationEntries/{service_id}"  # noqa: E501

    return self._get(path)


def get_service_orchestration_ipsla_settings(
    self,
    service_id: str,
) -> bool:
    """Get Service Orchestration service ipsla settings

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/ipslaSetting/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/ipslaSetting?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/ipslaSetting/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_ipsla_settings(
    self,
    service_id: str,
    source_interface: str,
    enable: bool = True,
    monitor_type: str = "http-monitor",
    destination: str = "sp-ipsla.silverpeak.cloud",
    http_timeout: int = 2,
    keepalive_interval: int = 5,
    up_threshold: int = 2,
    down_threshold: int = 3,
    interval: int = 60,
    sampling_window: int = 300,
    up_loss: int = 0,
    down_loss: int = 0,
    up_latency: int = 0,
    down_latency: int = 0,
    metric_combination: str = "metric-or",
    proxy_address: str = None,
    proxy_port: str = None,
    user_agent: str = None,
) -> bool:
    """Set Service Orchestration service tunnel settings. Default values
    are default values from Orchestrator when creating a new service.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/tunnelSetting/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param source_interface: Source interface name or label to source
      IPSLA traffic from, e.g. ``lan0`` or ``LOOPBACK``
    :type source_interface: str
    :param enable: ``True`` to Enable orchestration of IPSLA for service
    :type enable: bool, optional
    :param monitor_type: Monitor type for IPSLA, ``http-monitor`` or
      ``ip-monitor``, defaults to ``http-monitor``
    :type monitor_type: str, optional
    :param destination: Destination for IPSLA, can include multiple
      targets e.g., ``sp-ipsla.silverpeak.cloud,8.8.8.8,8.8.4.4``,
      defaults to ``sp-ipsla.silverpeak.cloud``
    :type destination: str, optional
    :param http_timeout: HTTP timeout value in seconds,
      defaults to ``2``
    :type http_timeout: int, optional
    :param keepalive_interval: Keepalive interval in seconds,
      defaults to ``5``
    :type keepalive_interval: int, optional
    :param up_threshold: Up threshold count, defaults to ``2``
    :type up_threshold: int, optional
    :param down_threshold: Down threshold count, defaults to ``3``
    :type down_threshold: int, optional
    :param interval: Test interval in seconds, defaults to ``60``
    :type interval: int, optional
    :param sampling_window: Sampling window in seconds,
      defaults to ``300``
    :type sampling_window: int, optional
    :param up_loss: Up loss %, only used if set to value greater than
      ``0``, defaults to ``0``
    :type up_loss: int, optional
    :param down_loss: Down loss %, only used if set to value greater
      than ``0``, defaults to ``0``
    :type down_loss: int, optional
    :param up_latency: Up latency in milliseconds, only used if set to
      value greater than ``0``, defaults to ``0``
    :type up_latency: int, optional
    :param down_latency: Down latency in milliseconds, only used if set
      to value greater than ``0``, defaults to ``0``
    :type down_latency: int, optional
    :param metric_combination: Combination of metrics, can be set to
      ``metric-and`` for AND logic, or set to ``metric-or`` for OR logic
    :type metric_combination: str, optional
    :param proxy_address: Proxy address for appliance to use, defaults
      to ``None``
    :type proxy_address: str, optional
    :param proxy_port: Proxy port for appliance to use, defaults
      to ``None``
    :type proxy_port: str, optional
    :param user_agent: User agent for appliance to use, defaults
      to ``None``
    :type user_agent: str, optional
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {
        "enableIpslaRuleOrchestration": enable,
        "thirdPartyIPSLARuleDestination": {
            "type": monitor_type,
            "destination": destination,
            "httpTimeout": http_timeout,
            "keepAliveInterval": keepalive_interval,
            "upThreshold": up_threshold,
            "downThreshold": down_threshold,
            "interval": interval,
            "samplingWindow": sampling_window,
            "upLoss": up_loss,
            "downLoss": down_loss,
            "upLatency": up_latency,
            "downLatency": down_latency,
            "metricCombination": metric_combination,
            "sourceInterface": source_interface,
        },
    }

    if proxy_address is not None:
        data["thirdPartyIPSLARuleDestination"]["proxyAddress"] = proxy_address
    if proxy_port is not None:
        data["thirdPartyIPSLARuleDestination"]["proxyPort"] = proxy_port
    if user_agent is not None:
        data["thirdPartyIPSLARuleDestination"]["userAgent"] = user_agent

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/ipslaSetting?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/ipslaSetting/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        return_type="bool",
    )


def get_service_orchestration_remote_endpoints(
    self,
    service_id: str,
) -> dict:
    """Get a Service Orchestration remote endpoints for service id

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/remoteEndpoints/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Returns dictionary of list of dictionaries for each remote
      endpoint defined for the service \n
      * keyword **remoteEndpoints** (`list`): List of remote endpoints\n
        * [`dict`]: Remote endpoint object \n
          * keyword **remoteEndpointId** (`int`): ID of remote endpoint
          * keyword **serviceId** (`int`): ID of service associated
          * keyword **remoteEndpointName** (`str`): Friendly name of
            remote endpoint
          * keyword **labelId** (`str`): Label id allowed to connect to
            this remote endpoint, allows `any`, otherwise uses a
            | delimited string e.g., ``1|2|3``
          * keyword **ipAddress** (`str`): IP address of remote endpoint
          * keyword **preSharedKey** (`str`): PSK for remote endpoint
          * keyword **probeIpAddress** (`str`): Probe IP address to
            monitor for this endpoint
          * keyword **backupEndpointId** (`str`): ID of backup remote
            endpoint as string
          * keyword **timestamp** (`int`): Timestamp of creation
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_remote_endpoints(
    self,
    service_id: str,
    remote_endpoints: list[dict],
) -> dict:
    """Create Service Orchestration remote endpoints for service id

    .. warning::
      This will replace all endpoints for the particular service id,
      use :func:`~pyedgeconnect.Orchestrator.add_service_orchestration_remote_endpoints`
      to add a new endpoint without affecting existing configured
      endpoints. To associate backup relationships between endpoints
      would need to add endpoints to first discover the resulting
      id values of the endpoints to include for the value of the
      ``backupEndpointId`` keyword in the dictionary.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/remoteEndpoints/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param remote_endpoints: Remote endpoint to delete \n
      * [`dict`]: Remote endpoint object \n
        * keyword **remoteEndpointId** (`int`): ID of remote endpoint
        * keyword **serviceId** (`int`): ID of service associated
        * keyword **remoteEndpointName** (`str`): Friendly name of
          remote endpoint
        * keyword **labelId** (`str`): Label id allowed to connect to
          this remote endpoint, allows `any`, otherwise uses a
          | delimited string e.g., ``1|2|3``
        * keyword **ipAddress** (`str`): IP address of remote endpoint
        * keyword **preSharedKey** (`str`): PSK for remote endpoint
        * keyword **probeIpAddress** (`str`): Probe IP address to
          monitor for this endpoint
        * keyword **backupEndpointId** (`str`): ID of backup remote
          endpoint as string
    :type remote_endpoint: list[dict]
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {"remoteEndpoints": remote_endpoints}

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def add_service_orchestration_remote_endpoints(
    self,
    service_id: str,
    remote_endpoints: list[dict],
) -> bool:
    """Add list of Service Orchestration remote endpoints for service id
    to existing endpoints. To associate backup relationships between
    endpoints would need to add endpoints to first discover the
    resulting id values of the endpoints to include for the value of the
    ``backupEndpointId`` keyword in the dictionary.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/remoteEndpoints/addEndpoints/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param remote_endpoints: Remote endpoint to delete remote endpoint\n
      * [`dict`]: Remote endpoint object \n
        * keyword **remoteEndpointId** (`int`): ID of remote endpoint
        * keyword **remoteEndpointName** (`str`): Friendly name of
          remote endpoint
        * keyword **labelId** (`str`): Label id allowed to connect to
          this remote endpoint, allows `any`, otherwise uses a
          | delimited string e.g., ``1|2|3``
        * keyword **ipAddress** (`str`): IP address of remote endpoint
        * keyword **preSharedKey** (`str`): PSK for remote endpoint
        * keyword **probeIpAddress** (`str`): Probe IP address to
          monitor for this endpoint
        * keyword **backupEndpointId** (`str`): ID of backup remote
          endpoint as string
    :type remote_endpoint: list[dict]
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    data = {"remoteEndpoints": remote_endpoints}

    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints/addEndpoints?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints/addEndpoints/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def delete_service_orchestration_remote_endpoints(
    self,
    service_id: str,
    remote_endpoint: dict,
) -> dict:
    """Delete a Service Orchestration remote endpoint for service id

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - DELETE
          - /thirdPartyServices/serviceOrchestration/remoteEndpoints/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param remote_endpoint: Remote endpoint to delete \n
      * keyword **remoteEndpointId** (`int`): ID of remote endpoint
      * keyword **serviceId** (`int`): ID of service associated
      * keyword **remoteEndpointName** (`str`): Friendly name of
        remote endpoint
      * keyword **labelId** (`str`): Label id allowed to connect to
        this remote endpoint, allows `any`, otherwise uses a
        | delimited string e.g., ``1|2|3``
      * keyword **ipAddress** (`str`): IP address of remote endpoint
      * keyword **preSharedKey** (`str`): PSK for remote endpoint
      * keyword **probeIpAddress** (`str`): Probe IP address to
        monitor for this endpoint
      * keyword **backupEndpointId** (`str`): ID of backup remote
        endpoint as string
      * keyword **timestamp** (`int`): Timestamp of creation
    :type remote_endpoint: dict
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndpoints/{service_id}"  # noqa: E501

    return self._delete(
        path,
        data=remote_endpoint,
    )


def get_service_orchestration_appliance_association(
    self,
    service_id: str,
) -> dict:
    """Get Service Orchestration remote endpoint to appliance
    association for service id

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - GET
          - /thirdPartyServices/serviceOrchestration/remoteEndPointAssociations/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :return: Dictionary of service id remote endpoint association to
      appliances e.g., ``{"52": ["0.NE","10.NE"]} \n
      * keyword **<remote_endpoint_id>** (`list[str]`): List of
        appliance id's / nepk values associated to this particular
        remote endpoint for this service, e.g., ``["0.NE","10.NE"]``
    :rtype: dict
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations/{service_id}"  # noqa: E501

    return self._get(path)


def set_service_orchestration_appliance_association(
    self,
    service_id: str,
    association: dict,
) -> bool:
    """Set Service Orchestration remote endpoint to appliance
    association for service id

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - thirdPartyServices
          - POST
          - /thirdPartyServices/serviceOrchestration/remoteEndPointAssociations/{serviceId}

    :param service_id: String integer id of the service to query
    :type service_id: str
    :param association: Dictionary of service id remote endpoint association to
      appliances e.g., ``{"52": ["0.NE","10.NE"]} \n
      * keyword **<remote_endpoint_id>** (`list[str]`): List of
        appliance id's / nepk values associated to this particular
        remote endpoint for this service
    :type association: dict
    :return: Returns True/False based on successful call
    :rtype: bool
    """  # noqa: W505
    if self.orch_version >= 9.3:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations?serviceId={service_id}"  # noqa: E501
    else:
        path = f"/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations/{service_id}"  # noqa: E501

    return self._post(
        path,
        data=association,
        return_type="bool",
    )
