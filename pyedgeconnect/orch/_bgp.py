# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# bgp : Gets bgp config and state information


def get_appliance_bgp_config(
    self,
    ne_id: str,
) -> dict:
    """Returns all appliance BGP configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/config/system/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP configuration
    :rtype: dict
    """
    # return self._get("/bgp/config/system/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/config/system?nePk={ne_id}"
    else:
        path = f"/bgp/config/system/{ne_id}"

    return self._get(path)


def get_appliance_bgp_config_all_vrfs(
    self,
    ne_id: str,
) -> dict:
    """Returns all appliance BGP configuration for all vrfs

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/config/allVrfs/system/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP configuration
    :rtype: dict
    """
    # return self._get("/bgp/config/allVrfs/system/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/config/allVrfs/system?nePk={ne_id}"
    else:
        path = f"/bgp/config/allVrfs/system/{ne_id}"

    return self._get(path)


def get_appliance_bgp_neighbors(
    self,
    ne_id: str,
) -> dict:
    """Returns appliance BGP neighbor configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/config/neighbor/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP neighbors
    :rtype: dict
    """
    # return self._get("/bgp/config/neighbor/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/config/neighbor?nePk={ne_id}"
    else:
        path = f"/bgp/config/neighbor/{ne_id}"

    return self._get(path)


def get_appliance_bgp_neighbors_all_vrfs(
    self,
    ne_id: str,
) -> dict:
    """Returns appliance BGP neighbor configuration

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/config/allVrfs/neighbor/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP neighbors
    :rtype: dict
    """
    # return self._get("/bgp/config/allVrfs/neighbor/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/config/allVrfs/neighbor?nePk={ne_id}"
    else:
        path = f"/bgp/config/allVrfs/neighbor/{ne_id}"

    return self._get(path)


def get_appliance_bgp_state(
    self,
    ne_id: str,
) -> dict:
    """Returns appliance BGP current state

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/state/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP state
    :rtype: dict
    """
    # return self._get("/bgp/state/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/state?nePk={ne_id}"
    else:
        path = f"/bgp/state/{ne_id}"

    return self._get(path)


def get_appliance_bgp_state_all_vrfs(
    self,
    ne_id: str,
) -> dict:
    """Returns appliance BGP current state

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - bgp
          - GET
          - /bgp/state/allVrfs/{neId}

    :param ne_id: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_id: str
    :return: Returns appliance BGP state
    :rtype: dict
    """
    # return self._get("/bgp/state/allVrfs/{}".format(ne_id))
    if self.orch_version >= 9.3:
        path = f"/bgp/state/allVrfs?nePk={ne_id}"
    else:
        path = f"/bgp/state/allVrfs/{ne_id}"

    return self._get(path)
