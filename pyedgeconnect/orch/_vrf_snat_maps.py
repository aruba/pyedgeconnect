# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# vrfSnatMaps : Inter-Segment S-NAT Rule


def get_snat_maps(
    self,
    ne_id: str,
    cached: bool,
) -> dict:
    """Get VRF SNAT Map defined on appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - vrfSnatMaps
          - GET
          - /snatMaps/{neId}?cached={cached}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns dictionary of SNAT maps
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/snatMaps?nePk={ne_id}&cached={cached}"
    else:
        path = f"/snatMaps/{ne_id}?cached={cached}"

    return self._get(path)
