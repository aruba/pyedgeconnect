# MIT License
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
#
# appliancesSoftwareVersions : ECOS software version


def get_appliance_software_version(
    self,
    ne_pk: str,
    cached: bool,
) -> list:
    """Get appliance software version information

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - appliancesSoftwareVersions
          - GET
          - /appliancesSoftwareVersions/{nePK}?cached={cached}

    :param ne_pk: Network Primary Key (nePk) of existing appliance,
        e.g. ``3.NE``
    :type ne_pk: str
    :param cached: ``True`` retrieves last known value to Orchestrator,
        ``False`` retrieves values directly from Appliance
    :type cached: bool
    :return: Returns list of dictionaries of software version
        information per partition. \n
        [`dict`]: Software version info object \n
            * keyword **partition** (`int`): integer of partition where
              software is installed
            * keyword **build_version** (`str`): software version number
            * keyword **build_time** (`str`): timetstamp of build
            * keyword **active** (`bool`): ``True`` if this partition is
              the active software
            * keyword **next_boot** (`bool`): ``True`` if this partition
              will be active for next boot
            * keyword **fallback_boot** (`bool`): ``True`` if this
              partition will boot if another active partition fails
    :rtype: list
    """
    if self.orch_version >= 9.3:
        path = f"/appliancesSoftwareVersions?nePk={ne_pk}&cached={cached}"
    else:
        path = f"/appliancesSoftwareVersions/{ne_pk}?cached={cached}"

    return self._get(path)
