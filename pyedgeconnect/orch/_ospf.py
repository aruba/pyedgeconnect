# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# ospf : apis for get config and state of ospf


def get_appliance_ospf_config(
    self,
    ne_id: str,
) -> dict:
    """Get appliance OSPF configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - ospf
          - GET
          - /ospf/config/system/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of OSPF configuration info
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/ospf/config/system?nePk={ne_id}"
    else:
        path = f"/ospf/config/system/{ne_id}"

    return self._get(path)


def get_appliance_ospf_interfaces_config(
    self,
    ne_id: str,
) -> dict:
    """
    Get appliance OSPF interfaces configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - ospf
          - GET
          - /ospf/config/interfaces/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of OSPF interfaces configuration info
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/ospf/config/interfaces?nePk={ne_id}"
    else:
        path = f"/ospf/config/interfaces/{ne_id}"

    return self._get(path)


def get_appliance_ospf_state(
    self,
    ne_id: str,
) -> dict:
    """Get appliance OSPF state

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - ospf
          - GET
          - /ospf/state/system/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of OSPF system state
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/ospf/state/system?nePk={ne_id}"
    else:
        path = f"/ospf/state/system/{ne_id}"

    return self._get(path)


def get_appliance_ospf_interfaces_state(
    self,
    ne_id: str,
) -> dict:
    """Get appliance OSPF interfaces state

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - ospf
          - GET
          - /ospf/state/interfaces/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of OSPF interfaces state
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/ospf/state/interfaces?nePk={ne_id}"
    else:
        path = f"/ospf/state/interfaces/{ne_id}"

    return self._get(path)


def get_appliance_ospf_neighbors_state(
    self,
    ne_id: str,
) -> dict:
    """Get appliance OSPF neighbors state

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - ospf
          - GET
          - /ospf/state/neighbors/{neId}

    :param ne_id: Appliance id in the format of integer.NE e.g. ``3.NE``
    :type ne_id: str
    :return: Returns dictionary of OSPF neighbors state
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/ospf/state/neighbors?nePk={ne_id}"
    else:
        path = f"/ospf/state/neighbors/{ne_id}"

    return self._get(path)
