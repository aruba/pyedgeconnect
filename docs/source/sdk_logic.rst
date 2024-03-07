=========================
 Function Flow Logic
=========================

.. code::

                ┌─Class:Orchestrator┐    ┌────────────Class:HttpCommon───────────────┐
                ┌───────────────────┐    ┌──────────────────┐    ┌───────────────────┐
                │                   │    │     _get()       │    │    _req_get()     │
    USER        │     EXAMPLE       ├─1──►     _post()      ├─2──►    _req_post()    │
    INPUT   ─►  │     FUNCTION      │    │     _put()       │    │    _req_put()     │
                │                   ◄─6──┼─┐   _delete() ┌──◄──3─┤    _req_delete()  │
                └───────────────────┘    └─▲─────────────┼──┘    └───────────────────┘
                                           │             │
                                           │             4
                                           5             │
                                           │   ┌─────────▼────────────┐
                                           │   │                      │
                                           └───┤  _handle_response()  │
                                               │                      │
                                               └──────────────────────┘



This class is the base class for processing HTTP requests from front-end
functions and handling responses back to the user.

The logic is the same for HTTP `GET`, `POST`, `PUT`, and `DELETE`. The
below example walks through processing a `GET`.

1. A function from
:class:`~pyedgeconnect.Orchestrator` or
:class:`~pyedgeconnect.EdgeConnect` makes a call to
:meth:`pyedgeconnect.HttpCommon._get` with the short path
(portion of the path that is unique to the function) and other optional
parameters such as ``expected_status`` or ``return_type`` if applicable.

2. The :meth:`pyedgeconnect.HttpCommon._get` function will check
that the requested ``return_type`` parameter is valid, then pass the
``api_path`` to :meth:`pyedgeconnect:HttpCommon:_req_get`. This
function appends the short path to the url prefix for the instance of
:class:`~pyedgeconnect.Orchestrator` or
:class:`~pyedgeconnect.EdgeConnect` and returns a response.

3. The response is returned back to
:meth:`pyedgeconnect.HttpCommon._get` and then along with the
short path, expected HTTP statuses, and data return type are passed to
:meth:`pyedgeconnect.HttpCommon._handle_response`.

4. The :meth:`pyedgeconnect.HttpCommon._handle_response`
will first check if the HTTP response code is within the expected
status. If the expected status code is outside of the expected
values it will be logged as an error. Default expected status is
``200``, though some functions are overridden to include an empty
``204`` as valid, among others.

The return value of the function will vary based on the expected
``return_type`` parameter. If ``return_type`` was ``json`` a dictionary
or list will be returned with the response values, ``text`` will return
response text, ``bool`` will return ``True`` or ``False``, and
``full_response`` will return the full requests.Request object.

When logging an error, the HTTP method and path used, the HTTP status
code, and response text will be written to the error log.

With an error and ``return_type`` of ``json``, a dictionary is returned
with the keys ``request`` for HTTP request method, ``api_path`` for the
API endpoint, ``status_code`` for HTTP response code, and ``text`` for
the response text.

Below is a snippet of this logic from
:meth:`pyedgeconnect.HttpCommon._handle_response` when handling
an unexpected status and treating it as an error.

.. code-block:: python

    if response.status_code not in expected_status:
        self.logger.error(...)

        if return_type == "json":
            return {
                "request": response.request,
                "api_path": api_path,
                "status_code": response.status_code,
                "text": response.text,
            }
        elif return_type == "text":
            return response.text
        elif return_type == "bool":
            return False
        elif return_type == "full_response":
            return response

5. The return is passed back to the originating
:meth:`pyedgeconnect.HttpCommon._get`

6. The return is passed back to the originating function called by the
user


Orchestrator 9.3+ API Changes:

To accomodate cross-compatability with the major API changes in
Orchestrator version 9.3 and beyond, additional logic was added
in the init & login functions to verify Orcehstrator version to then
check in submodule functions to utilize the correctly formatted endpoint
based on version.

Below you can see the logic on init if an API key is provided to
immediately check Orchestrator's version and log the major/minor
version numbers.

.. code-block::python

    # Check if Orchestrator version is 9.3+ if API Key provided
    if api_key != "":
        try:
            orch_info = self.get_orchestrator_server_brief()
            release = orch_info["release"]
            major = int(release.split(".")[0])
            minor = int(release.split(".")[1])
            self.orch_version = major + minor / 10
        except Exception as e:
            print(e)
            print(
                """
                Attempt to retrieve Orchestrator version failed
                Defaulting logic to pre-9.3 API endpoints
                """
            )
            # Orch Version not found, default to pre-9.3
            self.orch_version = 0.0

Similar logic is in the user login function in case an API key is not
provided upon init. Upon a successfull login the function will
perform the same query to Orchestrator and log the version information.

The Orchestrator submodules have been updated with logic to leverage the
Orchestrator version to create a valid endpoint based on the version.

Instead of the endpoint being directly in the POST, a new variable
``path`` is used to properly form the endpoint and query parameters
based on pre 9.3 or post 9.3 syntax:

.. code-block::python

    def appliance_post_api(
        self,
        ne_pk: str,
        url: str,
        data,
    ) -> dict:
        """<docstring ...>"""
        if self.orch_version >= 9.3:
            path = f"/appliance/rest?nePk={ne_pk}&url={url}"
        else:
            path = f"/appliance/rest/{ne_pk}/{url}"

        return self._post(
            path,
            data=data,
            expected_status=[200, 204],
            return_type="bool",
        )
