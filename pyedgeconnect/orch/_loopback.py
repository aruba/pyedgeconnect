# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# loopback : Gets Appliance Loopback interfaces config


def get_loopback_interfaes(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get configured loopback interfaces on Edge Connect appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - loopback
          - GET
          - /virtualif/loopback/{neId}?cached={cached}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of configured loopback interfaces
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/virtualif/loopback?nePk={ne_id}&cached={cached}"
    else:
        path = f"/virtualif/loopback/{ne_id}?cached={cached}"

    return self._get(path)
