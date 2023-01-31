# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# nexthops : Next hops
from __future__ import annotations


def get_appliance_nexthops(
    self,
) -> list[dict]:
    """Get appliance's data path next hops information

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - nexthops
          - GET
          - /nexthops

    :return: Returns list of dictionaries of next hop information \n
        * [`dict`]: list of next hop objects \n
          * keyword **nhop_ipver** (`str`): IP version for next hop,
            ``ipv4`` or ``ipv6``
          * keyword **source** (`str`): Next hop for data path WAN or
            LAN side
          * keyword **nhop_ip** (`str`): Next hop IP address
          * keyword **nhop_state** (`str`): Next hop reachable state,
            ``reachable`` or ``unreachable``
          * keyword **nhop_uptime** (`int`): Next hop uptime in
            milliseconds
          * keyword **nhop_ifname** (`str`): Data path interface this
            Next hop belong to, e.g. ``wan0``
    :rtype: list[dict]
    """
    return self._get("/nexthops")
