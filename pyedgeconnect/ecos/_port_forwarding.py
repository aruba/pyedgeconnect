# MIT License
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
#
# portForwarding : Port Forwarding Settings
from __future__ import annotations


def get_port_forwarding_rules(
    self,
) -> list[dict]:
    """Get port forwarding rules on this appliance

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - portForwarding
          - GET
          - /portForwarding

    :return: Returns list of dictionaries of each port forwarding rule
        configured on appliance \n
        * [`dict`]: List of port forwarding rule objects \n
          * keyword **srcSubnet** (`str`): Source subnet of the rule
          * keyword **destSubnet** (`str`): Destination subnet of the
            rule
          * keyword **destPort** (`str`): Destination port or port range
            of the rule, e.g., ``123`` or ``123-234``, and should be
            ``0`` for ICMP protocol, and should be ``0-65535`` for ANY
            protocol
          * keyword **protocol** (`str`): Protocol of the rule, could be
            any of ``UDP``, ``TCP``, ``ICMP`` and ``ANY``
          * keyword **targetIp** (`str`): If a packet header matches
            this rule, the packet would be translated to this new IP
            address
          * keyword **targetPort** (`str`): If a packet header matches
            this rule, the packet would be translated to this new port
            or port range
          * keyword **gms_marked** (`bool`): To indicate whether this
            rule was generated by GMS or by user
          * keyword **comment** (`str`): Comment
          * keyword **srcIf** (`str`): Source interface name
          * keyword **vrf_id** (`int`): vrf segment id
    :rtype: list[dict]
    """
    return self._get("/portForwarding")


def set_port_forwarding_rules(
    self,
    pfw_rules: list,
) -> bool:
    """Set port forwarding rules on this appliance

    .. warning::

        This will overwrite all existing port forwarding rules on
        appliance. If you're trying to append new rules to existing
        rules, first use
        :func:`~pyedgeconnect.EdgeConnect.get_port_forwarding_rules`
        to get existing rules, append new rules to the list, then post
        all the rules together with this function.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - portForwarding
          - POST
          - /portForwarding2

    :param pfw_rules: List of port forwarding rules to be configured
      on the appliance. \n
        * [`dict`]: Port forwarding rule list object \n
          * keyword **srcSubnet** (`str`): Source subnet of the rule
          * keyword **destSubnet** (`str`): Destination subnet of the
            rule
          * keyword **destPort** (`str`): Destination port or port range
            of the rule, e.g., ``123`` or ``123-234``, and should be
            ``0`` for ICMP protocol, and should be ``0-65535`` for ANY
            protocol
          * keyword **protocol** (`str`): Protocol of the rule, could be
            any of ``UDP``, ``TCP``, ``ICMP`` and ``ANY``
          * keyword **targetIp** (`str`): If a packet header matches
            this rule, the packet would be translated to this new IP
            address
          * keyword **targetPort** (`str`): If a packet header matches
            this rule, the packet would be translated to this new port
            or port range
          * keyword **gms_marked** (`bool`): To indicate whether this
            rule was generated by GMS or by user
          * keyword **comment** (`str`): Comment
          * keyword **srcIf** (`str`): Source interface name
          * keyword **vrf_id** (`int`): vrf segment id
    :type pfw_rules: list[dict]
    :return: If successful returns string of ``Successfully saved port
      forwarding rules.``
    :rtype: str
    """
    return self._post(
        "/portForwarding2",
        data=pfw_rules,
        return_type="text",
    )


def set_gms_marked_port_forwarding_rules(
    self,
    pfw_rules: list,
) -> bool:
    """Set GMS marked port forwarding rules on this appliance (as if
    they were configured by Orchestrator, greyed out in the UI until
    edited).

    .. warning::

        Rules added via this function will not persist if
        :func:`~pyedgeconnect.EdgeConnect.set_port_forwarding_rules` is
        used or if the rules are edited in the UI. The rules will not
        overwrite non-gms marked rules.

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - portForwarding
          - POST
          - /portForwarding2/gms

    :param pfw_rules: List of port forwarding rules to be configured
      on the appliance. \n
        * [`dict`]: Port forwarding rule list object \n
          * keyword **srcSubnet** (`str`): Source subnet of the rule
          * keyword **destSubnet** (`str`): Destination subnet of the
            rule
          * keyword **destPort** (`str`): Destination port or port range
            of the rule, e.g., ``123`` or ``123-234``, and should be
            ``0`` for ICMP protocol, and should be ``0-65535`` for ANY
            protocol
          * keyword **protocol** (`str`): Protocol of the rule, could be
            any of ``UDP``, ``TCP``, ``ICMP`` and ``ANY``
          * keyword **targetIp** (`str`): If a packet header matches
            this rule, the packet would be translated to this new IP
            address
          * keyword **targetPort** (`str`): If a packet header matches
            this rule, the packet would be translated to this new port
            or port range
          * keyword **gms_marked** (`bool`): To indicate whether this
            rule was generated by GMS or by user
          * keyword **comment** (`str`): Comment
          * keyword **srcIf** (`str`): Source interface name
          * keyword **vrf_id** (`int`): vrf segment id
    :type pfw_rules: list[dict]
    :return: If successful returns string of ``Successfully saved port
      forwarding rules.``
    :rtype: str
    """
    return self._post(
        "/portForwarding2",
        data=pfw_rules,
        return_type="text",
    )