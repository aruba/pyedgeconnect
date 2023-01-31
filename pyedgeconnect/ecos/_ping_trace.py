# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# pingTrace : Ping and Traceroute


def run_ping_or_traceroute(
    self,
    command: str,
    destination_ip_hostname: str,
    options: str,
) -> dict:
    """Run a ping or traceroute from appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - pingTrace
          - POST
          - /pingTrace

    :param command: Accepted values of ``ping`` or ``traceroute``
    :type command: str
    :param destination_ip_hostname: Destination IP or hostname to try
      to ping or traceroute to, e.g. ``8.8.8.8``
    :type destination_ip_hostname: str
    :param options: Ping or traceroute command options as you would use
      in the appliance UI. e.g., For ping specify an interface with
      ``-I wan0``
    :type options: str
    :return: Returns dictionary of process id, data, and status \n
        * keyword **pid** (`int`): Process ID to reference
        * keyword **data** (`str`): Current data from command, generally
          blank when just run
        * keyword **status** (`str`): Status of process, if currently
          running, ``True``, otherwise ``False``
    :rtype: dict
    """
    data = {
        "cmd": command,
        "ip_hostname": destination_ip_hostname,
        "options": options,
    }

    return self._post(
        "/pingTrace",
        data=data,
    )


def get_ping_or_traceroute(
    self,
    pid: int,
) -> dict:
    """Get the result of running the ping or traceroute commands on
    the appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - pingTrace
          - POST
          - /pingTrace/{pid}

    :param pid: Integer process ID of running ping or traceroute
    :type pid: int
    :return: Returns dictionary of process id, data, and status \n
        * keyword **pid** (`int`): Process ID to reference
        * keyword **data** (`str`): Current data from command
        * keyword **status** (`str`): Status of process, if currently
          running, ``True``, otherwise ``False``
    :rtype: dict
    """
    return self._get(f"/pingTrace/{pid}")


def stop_ping_or_traceroute(
    self,
    pid: int,
) -> str:
    """Stop the a current ping or traceroute commands on the appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - pingTrace
          - POST
          - /pingTrace/{pid}

    :param pid: Integer process ID of running ping or traceroute
    :type pid: int
    :return: Returns string of ``OK`` if successfull
    :rtype: dict
    """
    return self._delete(
        f"/pingTrace/{pid}",
        return_type="text",
    )
