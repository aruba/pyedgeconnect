# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# securityMaps : Gets Appliance Security Policies


def get_appliance_security_maps(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get security policies configured on the appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - securityMaps
          - GET
          - /securityMaps/{neId}?cached={cached}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of security maps
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/securityMaps?nePk={ne_id}&cached={cached}"
    else:
        path = f"/securityMaps/{ne_id}?cached={cached}"

    return self._get(path)
