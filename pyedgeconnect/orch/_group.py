# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# group : Manage appliance groups


def get_gms_groups(self) -> dict:
    """Get all appliance groups in Orchestrator

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - GET
          - /gms/group

    :return: Returns dictionary of all appliance groups in Orchestrator
    :rtype: dict
    """
    return self._get("/gms/group")


def get_gms_group(
    self,
    group_pk: str,
) -> dict:
    """Get appliance group in Orchestrator

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - GET
          - /gms/group/{id}

    :param group_pk: The appliance group identifier, e.g. ``0.Network``
        is root group, ``1.Network`` is internal use, ``2.Network`` is
        auto-discovered groups. ``3.Network`` and beyond is user-defined
        groups.
    :type group_pk: str
    :return: Returns dictionary of group details in Orchestrator \n
        * keyword **id** (`str`): Group Primary Key, e.g. ``3.Network``
        * keyword **name** (`str`): Unique name given to group
        * keyword **subType** (`int`): Network sub type: Root Group is
          ``0``, Auto discovered group is ``2``, and User defined group
          is ``3``
        * keyword **parentId** (`str`): Parent group Primary Key
        * keyword **backgroundImage** (`str`): Name of background
          image filename, e.g. ``data_net.png``
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/gms/group?id={group_pk}"
    else:
        path = f"/gms/group/{group_pk}"

    return self._get(path)


def update_gms_group(
    self,
    group_pk: str,
    group_name: str,
    background_image_file: str = "",
) -> bool:
    """Update appliance group in Orchestrator

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - POST
          - /gms/group/{id}

    :param group_pk: The appliance group identifier, e.g. ``3.Network``
        this cannot be changed from the original
    :type group_pk: str
    :param group_name: Name of the group. Must be unique.
    :type group_name: str
    :param background_image_file: Image filename for group,
        defaults to ""
    :type background_image_file: str, optional
    :return: Returns True/False based on successful call.
    :rtype: bool
    """
    data = {
        "id": group_pk,
        "name": group_name,
        "backgroundImage": background_image_file,
    }

    if self.orch_version >= 9.3:
        path = f"/gms/group?id={group_pk}"
    else:
        path = f"/gms/group/{group_pk}"

    return self._post(
        path,
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def delete_gms_group(
    self,
    group_pk: str,
) -> bool:
    """Delete an appliance group

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - DELETE
          - /gms/group/{id}

    :param group_pk: The appliance group identifier, e.g. ``3.Network``
    :type group_pk: str
    :return: Returns True/False based on successful call.
    :rtype: bool
    """
    if self.orch_version >= 9.3:
        path = f"/gms/group?id={group_pk}"
    else:
        path = f"/gms/group/{group_pk}"

    return self._delete(
        path,
        expected_status=[204],
        return_type="bool",
    )


def add_gms_group(
    self,
    group_name: str,
    parent_pk: str = "",
    background_image_file: str = "",
) -> bool:
    """Update appliance group in Orchestrator

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - POST
          - /gms/group/new

    :param group_name: Name of the group. Must be unique.
    :type group_name: str
    :param parent_pk: The appliance group identifier,
        e.g. ``3.Network``, "" will act as to root group, defaults to ""
    :type parent_pk: str, optional
    :param background_image_file: Image filename for group,
        defaults to ""
    :type background_image_file: str, optional
    :return: Returns True/False based on successful call.
    :rtype: bool
    """
    data = {
        "name": group_name,
        "parentId": parent_pk,
        "backgroundImage": background_image_file,
    }

    return self._post(
        "/gms/group/new",
        data=data,
        expected_status=[204],
        return_type="bool",
    )


def get_root_gms_group(self) -> dict:
    """Get root appliance group

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - group
          - GET
          - /gms/group/root

    :return: Returns dictionary of root appliance group, ``0.Network``
    :rtype: dict
    """
    return self._get("/gms/group/root")
