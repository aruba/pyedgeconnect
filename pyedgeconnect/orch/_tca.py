# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# tca : ECOS threshold crossing alerts


def get_appliance_tca(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get system threshold crossing alerts for appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - tca
          - GET
          - /tca/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of system tca configuration
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/tca?nePk={ne_id}&cached={cached}"
    else:
        path = f"/tca/{ne_id}?cached={cached}"

    return self._get(path)


def get_appliance_tunnel_tca(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get tunnel threshold crossing alerts for appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - tca
          - GET
          - /tca/tunnel/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of system tca configuration
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/tca/tunnel?nePk={ne_id}&cached={cached}"
    else:
        path = f"/tca/tunnel/{ne_id}?cached={cached}"

    return self._get(path)
