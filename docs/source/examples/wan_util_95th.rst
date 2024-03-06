.. wan_util_95th:


.. important::

    The following example is more complex code than the general examples,
    generating data and interacting with Orchestrator. Using and
    modifying these examples requires a greater understanding of python
    functions, handling variables, and additional tools such as Pandas.


.. note::

    The code referenced in this document and all published examples
    with pyedgeconnect are available from the GitHub repository within the
    `examples <https://github.com/aruba/pyedgeconnect/tree/main/examples>`_
    folder. Each example script contains logic to authenticate to the
    Orchestrator as documented in the authentication example.

    Clone the repository and download the examples with:

    .. code:: bash

        $ git clone https://github.com/aruba/pyedgeconnect.git

Collecting Appliance Timeseries Data for 95th Percentile Analysis
*******************************************************************

The focus of this example is analyzing system aggregate and
per-wan-interface 95th percentile utilization.

There are two main functions: collecting appliance data, and reporting
on previously collected data. We can only retrieve minute data from
Orchestrator for appliances based on the Statistics Retention for
Interface stats (default of 72 hours). We can retrieve data again
over time and run the reporting function across all of the collected
data to create a more accurate view of 95th percentile utilization over
a longer sample period.

This demo is not meant to replace long-term statistics retention or
exporting to a proper data storage solution / database. It
assists as a lightweight workflow to get a sense of utilization
without the overhead of deploying a database and query logic.

When running collection the code retrieves appliance interface
timeseries data from Orchestrator. The collection can be run for all
appliances, or limited to a specific appliance. It will only collect
timeseries data for WAN interfaces on appliances that currently have a
WAN label applied.

Deployment information including WAN interface comments (a common field
for including circuit ID's etc.) is collected and stored in a separate
metadata file for reference in the reporting function. The collection
can optionally be run to only update this deployment information file
to capture updated comments without having to go through collecting
the timeseries minute data for the interfaces.

When the timeseries data is collected, the data is augmented with
additional calculations including percent utilziation of the WAN
interface vs. the configured deployment values on the appliance as well
as interface comments, appliance license value, and timestamp convereted
to local timezone time based on the appliance location.

The timeseries data is then stored in a CSV file per-interface for the
collection period for analysis.

When run for reporting, all collected CSV files are brought into
Pandas DataFrames and merged per appliance. This allows calculation of
total system WAN utilization across all labels for a particular
timestamp.

The code is then able to run 95th Percentile reporting on a per-label
and aggregate system throughput level. All values are calculated on the
percent utilization of deployment/license values as to normalize
the values across appliances to easily identify outliers.

The calculated data report is exported to a simple CSV. Additional
filtering can be performed on the CSV data or using Excel or similar
to filter columns to top 10, certain value thresholds, or create charts.

Before running the code, make sure that the Python packages in addition
to ``pyedgeconnect`` are installed as this report leverages multiple
packages for processing the collected data.

These are referenced in the ``requirements.txt`` file in the
wan_util_95th example directory

.. code-block:: python

    pip install -r requirements.txt


Data Collection
===============================

.. note::

    The timeseries data gathered in this code example is the same data
    viewed in Orchestrator on the Interface Bandwidth Trends tab:
    ``Monitoring->Bandwidth->Overlays & Interfaces->Interface Trends``

The code will collect timeseries data for one or all appliances from
the current time going back 72 hours from Orchestrator.

The code will only collect deployment and timeseries data for appliances
that are currently in a reachable state to Orchestrator. When
polling :func:`pyedgeconnect.Orchestrator.get_appliances` the appliance
has to have a ``state`` with a value of ``1`` to be considered
reachable.

Storage/Analysis Implications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Contiguous minute data will represent 1,440 rows of data for a 24hr
period. When considering the 21 columns stored for each appliance
interface, that represents 30,240 datapoints per 24hr period for each
wan interface captured. With the default behavior capturing the maximum
72 hours of minute-data, this results in a CSV file usually around
~850-900KB per WAN interface. Interfaces with particularly long comment
strings can influence the per-file size as they are repeated per
timestamp in the raw data stored.

Extrapolating this to an environment with 100 appliances with 2 wan
interfaces each, a collection for the past 72 hours would generate
6,048,000 data points, 200 CSV files, and take up ~170MB of disk.

In a larger environment with 375 appliances with a total of 750
wan interfaces, 72 hours of data stores ~70M data points and takes
approximately 700MB of disk.

Data Calculations
^^^^^^^^^^^^^^^^^^
Calculated fields in addition to those natively from Orchestrator
per-wan-interface include:

#. ``tz_time``: This is the epoch timestamp from the data offset from
   the utc time to the appliance local timezone time translated to a
   datetime format ``"%m-%d-%Y%H:%M:%S"``
#. ``pct_outbound``: The percent utilization (0-100) of the outbound
   bytes transfered over that minute, converted to bits, averaged to a
   per-second value, and then divided by the deployment outbound value
   for that interface converted to like-bits from it's native value in
   Kbps.

    .. code-block:: python

        point["pct_outbound"] = (
            ((point["tx_bytes"] * 8) / 60)
            / (point["max_bw_tx"] * 1000)
            ) * 100

#. ``pct_inbound``: The percent utilization (0-100) of the inbound
   bytes transfered over that minute, converted to bits, averaged to a
   per-second value, and then divided by the deployment outbound value
   for that interface converted to like-bits from it's native value in
   Kbps.

    .. code-block:: python

        point["pct_inbound"] = (
            ((point["rx_bytes"] * 8) / 60)
            / (point["max_bw_rx"] * 1000)
        ) * 100

.. warning::

    There is no age out of data in existing csv files already
    collected, and so without cleaning up the collection, a large
    amount of data can be collected over time. This example is meant to
    inspire what's possible, not to handle a long-term reporting
    workflow where data may be stored into a database, aged out on a
    retention schedule and other production-quality attributes.


Exported Files
^^^^^^^^^^^^^^^^^

Data collection will create or replace existing file named
``appliance_interface_comments.json`` in the ``wan_int_tseries_data``
sub-directory.

It will also create CSV files for each labeled wan interface of each
appliance collected in the ``wan_int_tseries_data`` sub-directory. The
files are named in the format of
``<hostname>__<interface>_<label>.csv``.

Example: ``EC-01__wan0_INET1.csv``


Data Reporting
===============================

.. note::

    The output of this code is not meant to be a "production-ready"
    report, but provide guidance on ways to retrieve and manipulate
    EdgeConnect timeseries data for further analysis.

Data Filtering for Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As data is ingested back from the CSV files collected, there are
three primary points of filtering to reduce down the data to analyze.

#. Remove data that are outside of defined operating hours as per the
   variables ``BUSINESS_HOURS_START`` and ``BUSINESS_HOURS_END``. Each
   of these are represented as a 24hr clock in the format ``HH:MM``.

#. Remove data that are outside of defined operating weekdays as
   per the variables ``BUSINESS_DAY_START`` and ``BUSINESS_DAY_END``.
   Each of these are represented as an integer where ``0`` represents
   Monday, incrementing through ``6`` representing Sunday. The logic is
   to include the days, e.g. ``0-4`` would include Monday through
   Friday.

#. Remove duplicate timestamps for appliances with the same
   label/interface are dropped once all files for a single appliance
   have been merged.

Default Filtering values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- ``BUSINESS_HOURS_START`` = 09:00
- ``BUSINESS_HOURS_END`` = 17:00
- ``BUSINESS_DAY_START`` = 0
- ``BUSINESS_DAY_END`` = 4

Large Data Analysis Implications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As noted in the previous section, this collection can create large
amounts of data, which in turn can take longer to process.

Testing with different data sets filtering for local 9-5 Mon-Fri
estimated runtimes for reporting on data sets:

.. list-table:: Estimated Report Generation Times
   :header-rows: 1

   * - Appliances
     - WAN Interfaces
     - Report Time
   * - 16
     - 38
     - ~5sec
   * - 170
     - 358
     - ~22sec
   * - 380
     - 780
     - ~44sec

Certainly large environments will collect significantly more data and
in turn will take longer to process analysis on.

Data Calculations
^^^^^^^^^^^^^^^^^^
Calculated fields in addition to those natively
from Orchestrator per-wan-interface include:

- ``System Agg vs Deployment Out``: The 95th percentile of percent
  utilization (0-100) of the outbound data for a particular appliance
  compared against it's total system deployment maximum values.
- ``System Agg vs Deployment In``: The 95th percentile of percent
  utilization (0-100) of the inbound data for a particular appliance
  compared against it's total system deployment maximum values.
- ``System Agg vs License Out``: The 95th percentile of percent
  utilization (0-100) of the outbound data for a particular appliance
  compared against it's bandwidth license value.
- ``System Agg vs License In``: The 95th percentile of percent
  utilization (0-100) of the inbound data for a particular appliance
  compared against it's bandwidth license value.

.. code-block:: python

        system_df["system_dep_pct_inbound"] = round(
            (
                (system_df["rx_bytes"] * 8 / 60)
                / (system_df["system_max_inbound"] * 1000)
            ) * 100,
            2,
        )
        system_df["system_dep_pct_outbound"] = round(
            (
                (system_df["tx_bytes"] * 8 / 60)
                / (system_df["system_max_outbound"] * 1000)
            ) * 100,
            2,
        )
        system_df["system_lic_pct_inbound"] = round(
            (
                (system_df["rx_bytes"] * 8 / 60)
                / (system_df["license"] * 1000)
            ) * 100,
            2,
        )
        system_df["system_lic_pct_outbound"] = round(
            (
                (system_df["tx_bytes"] * 8 / 60)
                / (system_df["license"] * 1000)
            ) * 100,
            2,
        )

- ``<label> - Out``: The 95th percentile of percent utilization (0-100)
  of the outbound data for a particular appliance for a particular
  interface with the corresponding WAN label.
- ``<label> - In``: The 95th percentile of percent utilization (0-100)
  of the inbound data for a particular appliance for a particular
  interface with the corresponding WAN label.

.. code-block:: python

    for label in labels:
        label_df = df[df.label != label]
        label_analytics[f"{label} - inbound"] = round(
            label_df.pct_inbound.quantile(0.95), 2
        )
        label_analytics[f"{label} - outbound"] = round(
            label_df.pct_outbound.quantile(0.95), 2
        )


Exported Files
^^^^^^^^^^^^^^^^^

Report files will be saved in the in the ``wan_int_tseries_reports``
sub-directory.

The dataframe of 95th percentile calculations of percent utilization
against license, deployment, and interface deployment values. This file
is named ``<YYYY-MM-DD_HH_MM_SS>_report_dataframe.csv``.



Python Script & Orchestrator API calls
======================================


Runtime arguments
^^^^^^^^^^^^^^^^^

The python script has multiple runtime arguments defined. A user must
specify ``-c`` or ``-r`` at a minimum to guide collection or reporting
of data. The other arguments are optional.

All runtime arguments are as follows:

- ``-o`` or ``--orch``
    - Type: String
    - Desc: Specify the Orchestrator IP or FQDN, this can be used to
      be included in HTML report header as text without requiring
      connecting to Orchestrator for just reporting on previously
      collected data in CSV files.
    - Example values: ``192.0.2.100`` or ``orchestrator.<company>.com``
    - Default value: ``None``
- ``-a`` or ``--appliance``
    - Type: String
    - Desc: Specify a single appliance by hostname to either collect
      data for, or filter for on analysis of existing data files.
    - Default value: ``None``
- ``-c`` or ``--collect``
    - Type: Boolean
    - Desc: Run the collection portion of the scripting to collect data
      for one or all appliances
    - Default value: ``None``
- ``-d`` or ``--deployment``
    - Type: Boolean
    - Desc: Only collect deployment/interface comment data for updating
      metadata when reporting is run.
    - Default value: ``None``
- ``-r`` or ``--report``
    - Type: Boolean
    - Desc: Run the reporting/analysis portion of the scripting to
      analyze previously collected data files for one or all appliances.
    - Default value: ``None``
- ``-ll`` or ``--loglevel``
    - Type: String
    - Desc: Logging level for script, examples values include ``INFO``,
      ``DEBUG``, ``ERROR``, etc.
    - Default value: ``None``

Running the script to collect data for all appliances:

.. code-block:: bash

    python wan_util_95th.py -c

Running the script to collect data for single appliance:

.. code-block:: bash

    python wan_util_95th.py -c -a MY-appliance-01

Running the script to report data for all existing files:

.. code-block:: bash

    python wan_util_95th.py -r

Running the script to update deployment interface comments:

.. code-block:: bash

    python wan_util_95th.py -c -d


Orchestrator API calls
^^^^^^^^^^^^^^^^^^^^^^^^^^

The three API calls to Orchestrator (outside of authentication) are:

- :func:`pyedgeconnect.Orchestrator.get_appliances`
- :func:`pyedgeconnect.Orchestrator.get_appliance_deployment`
- :func:`pyedgeconnect.Orchestrator.get_timeseries_stats_interface_single_appliance`

The ``get_appliances`` function gets all appliances from Orchestrator to
be able to map hostnames with underlying NePK values, as well as
other metadata and state of appliance with Orchestrator.

The ``get_appliance_deployment`` will return the full deployment
configuration of the appliance including interface names, comments,
labels, per-interface as well as total system WAN bandwidth values
among other details.

The ``get_timeseries_stats_interface_single_appliance`` will return
timeseries data for interfaces on an appliance. This will return a
maximum of 10,000 datapoints and so offers multiple filters to
limit the scope of the query for traffic type, interface name, start
and end time of the data.