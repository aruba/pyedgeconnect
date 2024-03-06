import re

import requests


def sse_mgmt_auth(
    sse_workspace_name: str,
    sse_user: str,
    sse_password: str,
) -> dict:
    """Authenticate to SSE Management API with Cookie Auth

    :param sse_workspace_name: Workspace name, e.g. ``customerLab``
    :type sse_workspace_name: str
    :param sse_user: Username of user with permissions to create
        locations and IPSEC tunnels
    :type sse_user: str
    :param sse_password: Password for user
    :type sse_password: str,
    :return: Returns dictionary of base Management API url path, the
        session to use for future API calls, and the Tenant ID value \n
        * keyword **mgmt_base_url** (`str`): Base url including Tenant
          ID for Management API calls
        * keyword **mgmt_session** (`Requests.Session`): Established
          Requests session to the Management API
        * keyword **tenant_id** (`str`): Tenant ID to reference in
          body for location/tunnel creation
    :rtype: dict
    """
    # Instantiate session to SSE portal
    sse_mgmt_session = requests.Session()
    sse_mgmt_auth_base_url = "https://auth.axissecurity.com"

    # Base URL for authentication process to SSE Management API
    sse_api_auth = sse_mgmt_session.get(sse_mgmt_auth_base_url)
    # Obtain correlation ID for tracking session
    corr_id = sse_api_auth.headers["ax_cor"]
    sse_mgmt_session.headers["x-correlation-id"] = corr_id
    # Obtain relay state variable
    retrieve_relay_state = sse_mgmt_session.post(
        f"{sse_mgmt_auth_base_url}/workspace?workspaceName={sse_workspace_name}&corr_id={corr_id}&requestFullUrl=%2F"
    )
    relay_state = retrieve_relay_state.json()["relayState"]
    # Perform first phase of login with user/password
    sse_authenticate = sse_mgmt_session.post(
        f"{sse_mgmt_auth_base_url}/api/AuthApi/idp/auth",
        json={
            "username": sse_user,
            "password": sse_password,
            "relayState": relay_state,
            "correlationId": corr_id,
        },
        allow_redirects=False,
    )
    # Response returns 302 redirect with URL containing tenant ID value
    # redirectUrl in format of /idp/{tenant_id}/...
    # Split on / and pull 2nd element to get tenant id

    sse_tenant_id = sse_authenticate.json()["redirectUrl"].split("/")[2]
    # Obtain SAML response code
    saml_response = sse_mgmt_session.get(
        f"{sse_mgmt_auth_base_url}/idp/{sse_tenant_id}/redirect?RelayState={relay_state}",
    )
    # Parse SAML response code from HTML response
    saml_match_pattern = re.compile(
        r"<input type=\"hidden\" name=\"SAMLResponse\" value=\"(.*?)\">"
    )
    saml_value = re.findall(saml_match_pattern, saml_response.text)[0]
    # Perform final authentication with SAML value which will populate
    # cookie value
    sse_mgmt_session.post(
        f"{sse_mgmt_auth_base_url}/saml/callback",
        data={
            "SAMLResponse": saml_value,
            "RelaySTate": relay_state,
        },
    )

    # Set base URL for Management API calls
    sse_mgmt_base_url = f"https://manage.axissecurity.com/api/{sse_tenant_id}"

    return {
        "mgmt_base_url": sse_mgmt_base_url,
        "mgmt_session": sse_mgmt_session,
        "tenant_id": sse_tenant_id,
    }
