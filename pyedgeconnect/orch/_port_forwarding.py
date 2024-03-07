# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# portForwarding : Getting one ECOS port forwarding rules


def get_appliance_port_fowarding(
    self,
    ne_pk: str,
) -> dict:
    """Get port forwarding rules configured on Edge Connect appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - portForwarding
          - GET
          - /portForwarding/{neId}

    :param ne_pk: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of port forwarding rules
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/portForwarding?nePk={ne_pk}"
    else:
        path = f"/portForwarding/{ne_pk}"

    return self._get(path)
