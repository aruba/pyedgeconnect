# MIT License
# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
#
# health : Appliance health summary
from __future__ import annotations


def get_health_appliance_summary(
    self,
    ne_pk_list: list[str],
    start_time: int,
    end_time: int,
    overlay_id: int = -1,
    categories: list[str] = ["ALARM", "LOSS", "LATENCY", "JITTER", "MOS"],
) -> dict:
    """Returns health summary of specified appliances

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - POST
          - /health

    :param ne_pk_list: List of one or more appliance Network Primary
        Keys (nePk), e.g. ``["3.NE","5.NE"]``
    :type ne_pk_list: list[str]
    :param start_time: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting time boundary of data time range
    :type start_time: int
    :param end_time: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the ending time boundary of data time range
    :type end_time: int
    :param overlay_id: Numeric ID of overlay to query for, ``-1`` for
        all overlays, Defaults to ``-1``
    :type overlay_id: int
    :param categories: Categories of health data to include in summary.
        Defaults to list of all options
        ``["ALARM", "LOSS", "LATENCY", "JITTER", "MOS"]``
    :type categories: list[str], optional
    :return: Returns dictionary of alarm summary for period specified.
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        data = {
            "nePks": ne_pk_list,
            "from": start_time,
            "overlayId": overlay_id,
            "to": end_time,
            "verticals": categories,
        }
    else:
        data = {
            "applianceIds": ne_pk_list,
            "from": start_time,
            "overlayId": overlay_id,
            "to": end_time,
            "verticals": categories,
        }

    return self._post(
        "/health",
        data=data,
    )


def get_health_alarm_summary(
    self,
    ne_pk: str,
    start_time: int,
    end_time: int,
) -> dict:
    """Returns summary of alarms for a given appliance for that time
    period

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/alarmPeriodSummary

    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param start_time: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting time boundary of data time range
    :type start_time: int
    :param end_time: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the ending time boundary of data time range
    :type end_time: int
    :return: Returns dictionary of alarm summary for period specified.\n
        * keyword **<alarm_cat>** (`dict`): object for alarm severity
          details, e.g. key of `critical` or `major` will have a
          value of ``null`` if there aren't any alarms of that
          severity \n
            * keyword **sequenceId** (`int`): Alarm seq id, e.g. ``5``
            * keyword **description** (`str`): Alarm description
            * keyword **time** (`int`): Epoch timestamp of alarm
        * keyword **alarmCountsInPeriod** (`dict`): Object of alarm
          summary \n
            * keyword **CRITICAL** (`int`): Count of critical alarms,
              optional and won't be included if count is 0
            * keyword **MAJOR** (`int`): Count of major alarms,
              optional and won't be included if count is 0
            * keyword **MINOR** (`int`): Count of minor alarms,
              optional and won't be included if count is 0
            * keyword **WARNING** (`int`): Count of warning alarms,
              optional and won't be included if count is 0
    :rtype: dict
    """
    if self.orch_version >= 9.3:
        path = f"/health/alarmPeriodSummary?nePk={ne_pk}&from={start_time}&to={end_time}"
    else:
        path = f"/health/alarmPeriodSummary?applianceId={ne_pk}&from={start_time}&to={end_time}"

    return self._get(path)


def get_health_threshold_config(
    self,
) -> dict:
    """Returns health threshold configurations

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/healthThresholdConfig

    :return: Returns dictionary of configured health threshold limits
      for alarms, bwUtilization, jitter, latency, mos, and packetLoss.
    :rtype: dict
    """
    return self._get("/health/healthThresholdConfig")


def set_health_threshold_config(
    self,
    alarm_critical: bool,
    alarm_major: bool,
    alarm_minor: bool,
    alarm_warning: bool,
    bw_good: float,
    bw_ok: float,
    jitter_good: float,
    jitter_ok: float,
    latency_good: float,
    latency_ok: float,
    mos_good: float,
    mos_ok: float,
    packet_loss_good: float,
    packet_loss_ok: float,
    all_thresholds: dict = None,
) -> dict:
    """Update health threshold configurations

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - POST
          - /health/healthThresholdConfig

    :param alarm_critical: Include critical alarms in health status
    :type alarm_critical: bool
    :param alarm_major: Include major alarms in health status
    :type alarm_major: bool
    :param alarm_minor: Include minor alarms in health status
    :type alarm_minor: bool
    :param alarm_warning: Include warning alarms in health status
    :type alarm_warning: bool
    :param bw_good: Threshold for great to good for integer percent
        bandwidth utilization, e.g., ``95.0`` is 95%
    :type bw_good: float
    :param bw_ok: Threshold for good to ok for integer percent
        bandwidth utilization,  e.g., ``95.0`` is 95%
    :type bw_ok: float
    :param jitter_good: Threshold for great to good for jitter,
         e.g., ``95.0`` is 95ms
    :type jitter_good: float
    :param jitter_ok: Threshold for good to ok for jitter,
        e.g., ``95.0`` is 95ms
    :type jitter_ok: float
    :param latency_good: Threshold for great to good for latency,
        e.g., ``95.0`` is 95ms
    :type latency_good: float
    :param latency_ok: Threshold for good to ok for latency,
        e.g., ``95.0`` is 95ms
    :type latency_ok: float
    :param mos_good: Threshold for great to good for MOS score,
        e.g., ``3.5`` is 3.5
    :type mos_good: float
    :param mos_ok: Threshold for good to ok for MOS score,
        e.g., ``3.5`` is 3.5
    :type mos_ok: float,
    :param packet_loss_good: Threshold for great to good for integer
        percent packet loss, e.g., ``95.0`` is 95%
    :type packet_loss_good: float
    :param packet_loss_ok: Threshold for good to ok for integer
        percent packet loss, e.g., ``95.0`` is 95%
    :type packet_loss_ok: float
    :param all_thresholds: An optional dictionary object to pass the
        entire dictionary of thresholds as a single paramter. Convenient
        if you're capturing existing thresholds from
        :func:`~pyedgeconnect.Orchestrator.get_health_threshold_config`,
        as the other parameters are all required, they must be included
        as to avoid accidentally setting defaulted values, but they
        will be ignored if the ``all_thresholds`` paramter is included.
        Defaults to None
    :type all_thresholds: dict, optional
    :return: Returns dictionary of configured health threshold limits
      for alarms, bwUtilization, jitter, latency, mos, and packetLoss.
    :rtype: dict
    """
    if all_thresholds is None:
        data = {
            "alarm": {
                "critical": alarm_critical,
                "major": alarm_major,
                "minor": alarm_minor,
                "warning": alarm_warning,
            },
            "bwUtilization": {
                "goodLimit": bw_good,
                "okLimit": bw_ok,
            },
            "jitter": {
                "goodLimit": jitter_good,
                "okLimit": jitter_ok,
            },
            "latency": {
                "goodLimit": latency_good,
                "okLimit": latency_ok,
            },
            "mos": {
                "goodLimit": mos_good,
                "okLimit": mos_ok,
            },
            "packetLoss": {
                "goodLimit": packet_loss_good,
                "okLimit": packet_loss_ok,
            },
        }
    else:
        data = all_thresholds

    return self._post(
        "/health/healthThresholdConfig",
        data=data,
    )


def get_health_jitter(
    self,
    ne_pk: str,
    timestamp: int,
    overlay_id: int = -1,
) -> dict:
    """Returns summary of jitter for a given appliance for that hour

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/jitterPeriodSummary

    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param timestamp: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting hour boundary of data time range
    :type timestamp: int
    :param overlay_id: Numeric ID of overlay to query for, ``-1`` for
        all overlays, Defaults to ``-1``
    :type overlay_id: int
    :return: Returns dictionary of jitter health summary \n
        * keyword **criticalMins** (`int`): Minutes of critical during
          the hour, i.e., time spent above the ``ok`` threshold
        * keyword **healthStatus** (`str`): ``HEALTHY`` if determined to
          meet health critera
        * keyword **majorMins** (`int`): Minutes of major during
          the hour, i.e., time spent above the ``good`` threshold and
          below ``ok`` threshold
        * keyword **max** (`int`): Maximum observed value during the
          hour
        * keyword **normalMins** (`int`): Minutes of normal value during
          the hour, i.e. time spent below the ``good`` threshold
        * keyword **tunnelId** (`str`): Alias of respective tunnel that
          is violating a threshold
    :rtype: dict
    """
    return self._get(
        f"/health/jitterPeriodSummary?applianceId={ne_pk}&time={timestamp}&overlayId={overlay_id}"  # noqa: W505
    )


def get_health_latency(
    self,
    ne_pk: str,
    timestamp: int,
    overlay_id: int = -1,
) -> dict:
    """Returns summary of latency for a given appliance for that hour

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/latencyPeriodSummary

    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param timestamp: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting hour boundary of data time range
    :type timestamp: int
    :param overlay_id: Numeric ID of overlay to query for, ``-1`` for
        all overlays, Defaults to ``-1``
    :type overlay_id: int
    :return: Returns dictionary of latency health summary \n
        * keyword **criticalMins** (`int`): Minutes of critical during
          the hour, i.e., time spent above the ``ok`` threshold
        * keyword **healthStatus** (`str`): ``HEALTHY`` if determined to
          meet health critera
        * keyword **majorMins** (`int`): Minutes of major during
          the hour, i.e., time spent above the ``good`` threshold and
          below ``ok`` threshold
        * keyword **max** (`int`): Maximum observed value during the
          hour
        * keyword **normalMins** (`int`): Minutes of normal value during
          the hour, i.e. time spent below the ``good`` threshold
        * keyword **tunnelId** (`str`): Alias of respective tunnel that
          is violating a threshold
    :rtype: dict
    """
    return self._get(
        f"/health/latencyPeriodSummary?applianceId={ne_pk}&time={timestamp}&overlayId={overlay_id}"  # noqa: W505
    )


def get_health_loss(
    self,
    ne_pk: str,
    timestamp: int,
    overlay_id: int = -1,
) -> dict:
    """Returns summary of latency for a given appliance for that hour

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/lossPeriodSummary

    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param timestamp: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting hour boundary of data time range
    :type timestamp: int
    :param overlay_id: Numeric ID of overlay to query for, ``-1`` for
        all overlays, Defaults to ``-1``
    :type overlay_id: int
    :return: Returns dictionary of packet loss health summary \n
        * keyword **criticalMins** (`int`): Minutes of critical during
          the hour, i.e., time spent above the ``ok`` threshold
        * keyword **healthStatus** (`str`): ``HEALTHY`` if determined to
          meet health critera
        * keyword **majorMins** (`int`): Minutes of major during
          the hour, i.e., time spent above the ``good`` threshold and
          below ``ok`` threshold
        * keyword **maxLossPercentage** (`float`): Maximum observed
          value during the hour
        * keyword **normalMins** (`int`): Minutes of normal value during
          the hour, i.e. time spent below the ``good`` threshold
        * keyword **tunnelId** (`str`): Alias of respective tunnel that
          is violating a threshold
    :rtype: dict
    """
    return self._get(
        f"/health/lossPeriodSummary?applianceId={ne_pk}&time={timestamp}&overlayId={overlay_id}"  # noqa: W505
    )


def get_health_mos(
    self,
    ne_pk: str,
    timestamp: int,
    overlay_id: int = -1,
) -> dict:
    """Returns summary of latency for a given appliance for that hour

    .. list-table::
        :header-rows: 1

        * - Swagger Section
          - Method
          - Endpoint
        * - health
          - GET
          - /health/mosPeriodSummary

    :param ne_pk: Network Primary Key (nePk) of appliance, e.g. ``3.NE``
    :type ne_pk: str
    :param timestamp: Long(Signed 64 bits) value of seconds since EPOCH
        time indicating the starting hour boundary of data time range
    :type timestamp: int
    :param overlay_id: Numeric ID of overlay to query for, ``-1`` for
        all overlays, Defaults to ``-1``
    :type overlay_id: int
    :return: Returns dictionary of MOS health summary \n
        * keyword **criticalMins** (`int`): Minutes of critical during
          the hour, i.e., time spent above the ``ok`` threshold
        * keyword **healthStatus** (`str`): ``HEALTHY`` if determined to
          meet health critera
        * keyword **majorMins** (`int`): Minutes of major during
          the hour, i.e., time spent above the ``good`` threshold and
          below ``ok`` threshold
        * keyword **max** (`int`): Maximum observed value during the
          hour
        * keyword **normalMins** (`int`): Minutes of normal value during
          the hour, i.e. time spent below the ``good`` threshold
        * keyword **tunnelId** (`str`): Alias of respective tunnel that
          is violating a threshold
    :rtype: dict
    """
    return self._get(
        f"/health/mosPeriodSummary?applianceId={ne_pk}&time={timestamp}&overlayId={overlay_id}"  # noqa: W505
    )
