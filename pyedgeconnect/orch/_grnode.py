# MIT License
# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
#
# grnode : Manage appliance locations


def get_all_appliance_locations(self) -> list:
    """Get all appliance graphical node location details (map position)

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - GET
          - /gms/grNode

    :return: Returns list of dictionaries with appliance details. \n
        [`dict`]: appliance detail object \n
            * keyword **id** (`str, optional`): ID, assigned by
              Orchestrator like ``1.GrNode``
            * keyword **groupId** (`str`): ID of the group belonged to
            * keyword **sourceId** (`str`): The source ID. For an
              appliance expect nePk values like ``3.NE``. For groups,
              expect group ID like ``10.Network``
            * keyword **appliance** (`bool`): ``True`` for an Appliance
              and ``False`` for Group
            * keyword **wx** (`int`): Coordinates X in map window
            * keyword **wy** (`int`): Coordinates Y in map window
            * keyword **latitude** (`float`): Latitude
            * keyword **longitude** (`float`): Longitude
    :rtype: list
    """
    return self._get("/gms/grNode")


def get_appliance_location(
    self,
    gr_node_pk: str,
) -> dict:
    """Get appliance graphical node location details (map position)

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - grnode
          - GET
          - /gms/grNode/{grNodePk}

    :param gr_node_pk: The appliance graphical node identifier,
        e.g. ``0.GrNode``
    :type gr_node_pk: str
    :return: Returns dictionary with appliance details \n
        * keyword **id** (`str, optional`): ID, assigned by
          Orchestrator, e.g. ``1.GrNode``
        * keyword **groupId** (`str`): ID of the group belonged to
        * keyword **sourceId** (`str`): The source ID. For an
          appliance expect nePk values like ``3.NE``. For groups, expect
          group ID like ``10.Network``
        * keyword **appliance** (`bool`): ``True`` for an Appliance and
          ``False`` for Group
        * keyword **wx** (`int`): Coordinates X in map window
        * keyword **wy** (`int`): Coordinates Y in map window
        * keyword **latitude** (`float`): Latitude
        * keyword **longitude** (`float`): Longitude
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/gms/grNode?grNodePk={gr_node_pk}"
    else:
        path = f"/gms/group/{gr_node_pk}"

    return self._get(path)


def update_appliance_location_grnodepk(
    self,
    gr_node_pk: str,
    wx: int,
    wy: int,
    latitude: float,
    longitude: float,
) -> bool:
    """Update appliance location graphical information by graphical
    node id

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - grnode
          - POST
          - /gms/grNode/{grNodePk}

    :param gr_node_pk: The appliance graphical node identifier,
        e.g. ``0.GrNode``
    :type gr_node_pk: str
    :param wx: X Coordinates in map window
    :type wx: int
    :param wy: Y Coordinates in map window
    :type wy: int
    :param latitude: Latitude coordinates
    :type latitude: float
    :param longitude: Latitude coordinates
    :type longitude: float
    :return: Returns True/False based on successful call.
    :rtype: bool
    """
    data = {"wx": wx, "wy": wy, "latitude": latitude, "longitude": longitude}

    if self.orch_version >= 9.3:
        path = f"/gms/grNode?grNodePk={gr_node_pk}"
    else:
        path = f"/gms/group/{gr_node_pk}"

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def update_appliance_location_nepk(
    self,
    ne_pk: str,
    wx: int,
    wy: int,
    latitude: float,
    longitude: float,
) -> bool:
    """Update appliance location graphical information by Network
    Primary Key (nePk)

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - grnode
          - POST
          - /gms/grNode/forNePk/{nePk}

    :param ne_pk: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_pk: str
    :param wx: X Coordinates in map window
    :type wx: int
    :param wy: Y Coordinates in map window
    :type wy: int
    :param latitude: Latitude coordinates
    :type latitude: float
    :param longitude: Latitude coordinates
    :type longitude: float
    :return: Returns True/False based on successful call.
    :rtype: bool
    """
    data = {"wx": wx, "wy": wy, "latitude": latitude, "longitude": longitude}

    if self.orch_version >= 9.3:
        path = f"/gms/grNode/forNePk?nePk={ne_pk}"
    else:
        path = f"/gms/group/forNePk/{ne_pk}"

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )
