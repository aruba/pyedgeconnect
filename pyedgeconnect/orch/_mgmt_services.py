# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# mgmtServices : Management Services


def get_mgmt_services(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get Edge Connect appliance management services configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - mgmtServices
          - GET
          - /mgmtServices/{neId}?cached={cached}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of configured management services \n
        * keyword **<service_name>** (`dict`): service detail object \n
            * keyword **self** (`str`): Name of service
            * keyword **displayName** (`str`): Display name of service
            * keyword **srcinf** (`str`): Interface for source IP
              address or label of applications
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/mgmtServices?nePk={ne_id}&cached={cached}"
    else:
        path = f"/mgmtServices/{ne_id}?cached={cached}"

    return self._get(path)
