# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# group : Cluster information


def get_cluster_state(self, cluster_name: str, cached: bool) -> dict:
    """Get the state of a cluster.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - GET
          - /cluster

    :param cluster_name: Site / Cluster Name
    :type cluster_name: str
    :param cached: Boolean indicating whether to get data from cache (true)
        or from appliance (false)
    :type cached: bool
    :return: Returns dictionary of cluster state information \n
        * keyword **<siteName>** (`dict`): Dictionary with site information \n
            * keyword **siteName** (`str`): Name of the site/cluster \n
            * keyword **inSync** (`bool`): Whether the cluster is in sync \n
            * keyword **nonce** (`float`): Nonce value for the cluster \n
            * keyword **siteApplianceInterfaceIps** (`dict`): Dictionary of appliance \n
                interface IPs keyed by network primary key (nePk) \n
                * keyword **<nePk>** (`dict`): Dictionary with appliance information \n
                    * keyword **applianceName** (`str`): Name of the appliance \n
                    * keyword **interfaceLabel** (`str`): Label of the interface \n
                    * keyword **interfaceName** (`str`): Name of the interface \n
                    * keyword **state** (`dict`): State information for the interface \n
                        * keyword **peerIPStatusList** (`list[dict]`): List of peer IP statuses \n
                            * keyword **peerIP** (`str`): IP address of the peer \n
                            * keyword **peerIPState** (`str`): State of the peer IP \n
                        * keyword **cluster** (`bool`): Whether clustering is enabled \n
                        * keyword **flow_redir** (`bool`): Whether flow redirection is enabled \n
                        * keyword **wait_time** (`float`): Wait time value \n
                        * keyword **interface** (`str`): Interface name \n
                        * keyword **user_sync** (`bool`): Whether user sync is enabled \n
                    * keyword **ip** (`str`): IP address of the interface \n
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster state is only supported on Orchestrator 9.5 and above"
        )
    else:
        path = f"/cluster?clusterName={cluster_name}&cached={cached}"

    return self._get(path)


def get_cluster_alarm_count(self) -> dict:
    """Get the alarm count for the cluster.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - GET
          - /cluster/alarmCount

    :return: Returns dictionary containing alarm count information for the cluster
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster alarm count is only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/alarmCount"

    return self._get(path)


def get_all_cluster_profiles(self) -> list:
    """Get all cluster profiles.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - GET
          - /cluster/profiles

    :return: Returns list of cluster profiles \n
        * Each profile is a dictionary containing: \n
            * keyword **id** (`str`): Unique identifier for the profile\n
            * keyword **name** (`str`): Name of the profile\n
            * keyword **interfaceLabel** (`str`): Label of the interface\n
            * keyword **flowRedirection** (`str`): Flow redirection setting\n
            * keyword **userSessionSync** (`str`): User session synchronization setting\n
            * keyword **waitTime** (`int`): Wait time value in milliseconds\n
            * keyword **isEdgeHaProfile** (`bool`): Whether the profile is an Edge HA profile\n
    :rtype: list
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profiles are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/profiles"

    return self._get(path)


def add_cluster_profiles(self, profiles: list) -> dict:
    """Add one or more cluster profiles.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - POST
          - /cluster/profiles

    :param profiles: List of profile dictionaries to add\n
        Each profile dictionary should contain:\n
            * keyword **name** (`str`): Name of the profile\n
            * keyword **interfaceLabel** (`str`): Label of the interface\n
            * keyword **flowRedirection** (`str`): Flow redirection setting\n
            * keyword **userSessionSync** (`str`): User session synchronization setting\n
            * keyword **waitTime** (`int`): Wait time value in milliseconds\n
    :type profiles: list\n
    :return: Returns dictionary indicating success status\n
        * keyword **success** (`bool`): Whether the operation was successful\n
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profiles are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/profiles"

    return self._post(path, data=profiles)


def update_cluster_profile(self, profile: dict) -> dict:
    """Update an existing cluster profile.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - PUT
          - /cluster/profiles

    :param profile: Dictionary containing profile information to update
        Must contain:
            * keyword **id** (`str`): Unique identifier of the profile to update
            * keyword **name** (`str`): Updated name of the profile
            * keyword **interfaceLabel** (`str`): Updated label of the interface
            * keyword **flowRedirection** (`str`): Updated flow redirection setting
            * keyword **userSessionSync** (`str`): Updated user session synchronization setting
            * keyword **waitTime** (`int`): Updated wait time value in milliseconds
    :type profile: dict
    :return: Returns dictionary indicating success status
        * keyword **success** (`bool`): Whether the operation was successful
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profiles are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/profiles"

    return self._put(path, data=profile)


def delete_cluster_profile(self, profile_id: str) -> dict:
    """Delete a cluster profile.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - DELETE
          - /cluster/profiles

    :param profile_id: Unique system generated Cluster Profile Id to delete
    :type profile_id: str
    :return: Returns dictionary indicating success status
        * keyword **success** (`bool`): Whether the operation was successful
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profiles are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = f"/cluster/profiles?profileId={profile_id}"

    return self._delete(
        path,
        expected_status=[200],
        return_type="bool",
    )


def get_all_cluster_profile_mappings(self) -> dict:
    """Get all cluster profile mappings.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - GET
          - /cluster/profileMapping

    :return: Returns a dictionary where keys are cluster profile IDs and values are lists
             of entities (like folders, processes, etc.) mapped to that profile
        * key **<clusterProfileId>** (`list`): List of entity IDs mapped to the profile
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profile mappings are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/profileMapping"

    return self._get(path)


def update_cluster_profile_mapping(self, mappings: dict) -> dict:
    """Update cluster profile mappings.

    Updates only the site mapping in the provided data. Existing mappings not included in the
    request will remain unchanged.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - PUT
          - /cluster/profileMapping

    :param mappings: Dictionary where keys are cluster profile IDs and values are lists
                    of entity IDs to be mapped to that profile
        * key **<clusterProfileId>** (`list`): List of entity IDs to map to the profile
    :type mappings: dict
    :return: Returns dictionary indicating success status
        * keyword **success** (`bool`): Whether the operation was successful
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Cluster profile mappings are only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/profileMapping"

    return self._put(path, data=mappings)


def initialize_edge_ha_cluster(self, appliance_ids: list) -> dict:
    """Initialize appliances for EdgeHA cluster.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - cluster
          - POST
          - /cluster/initForEdgeHA

    :param appliance_ids: List of appliance IDs to initialize for Edge HA cluster
    :type appliance_ids: list
    :return: Returns dictionary indicating success status
        * keyword **success** (`bool`): Whether the operation was successful
    :rtype: dict
    """

    if self.orch_version < 9.5:
        raise ValueError(
            "Edge HA cluster initialization is only supported on Orchestrator 9.5 and above"
        )
    else:
        path = "/cluster/initForEdgeHA"

    return self._post(path, data=appliance_ids)