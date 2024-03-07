.. boost timeseries:


.. note::

    The code referenced in this document and all published examples
    with pyedgeconnect are available from the GitHub repository within the
    `examples <https://github.com/aruba/pyedgeconnect/tree/main/examples>`_
    folder. Each example script contains logic to authenticate to the
    Orchestrator as documented in the authentication example.

    Clone the repository and download the examples with:

    .. code:: bash

        $ git clone https://github.com/aruba/pyedgeconnect.git

Collecting Appliance Timeseries Data for Boost Utilization
*******************************************************************

The focus of this example is retrieving appliance Boost utilization
and converting the Bytes Boosted per minute data into estimated
average Kbps. This helps compare the values against the configured
values which are already in Kbps units.

We can only retrieve minute data from Orchestrator for appliances based
on the Statistics Retention for default of 72 hours. We can retrieve
more data over time to create a more accurate view of utilization over
a longer sample period.

This demo is not meant to replace long-term statistics retention or
exporting to a proper data storage solution / database. It
assists as a lightweight workflow to get a sense of utilization
without the overhead of deploying a database and query logic.

When running collection the code retrieves appliance Boost
timeseries data from Orchestrator. The collection can be run for all
appliances, or limited to a specific appliance.

When the timeseries data is collected, the data is augmented with
additional calculation to estimate Kbps rates.

To convert the Bytes Boosted in a minute to an estimated Kbps rate
the raw value is multipled by 8 to convert to bits, divided by 60 to
convert to seconds, and then divided by 1000 to convert to Kilobits.

Simplified into a single step, multiply the bytes by 0.0001333

The timeseries data is then stored in a CSV file per-appliance for the
collection period for analysis.

Before running the code, make sure that the Python packages in addition
to ``pyedgeconnect`` are installed as this script leverages the
``pandas`` package for processing the collected data.

These are referenced in the ``requirements.txt`` file in the
boost_timeseries example directory

.. code-block:: python

    pip install -r requirements.txt


Data Collection
===============================

.. note::

    The timeseries data gathered in this code example is the same data
    viewed in Orchestrator on the Boost Trends tab:
    ``Monitoring->Bandwidth->Boost->Summary``

The code will collect timeseries data for one or all appliances from
the current time going back 72 hours from Orchestrator.

The code will only collect Boost timeseries data for appliances
that are currently in a reachable state to Orchestrator. When
polling :func:`pyedgeconnect.Orchestrator.get_appliances` the appliance
has to have a ``state`` with a value of ``1`` to be considered
reachable.

Storage/Analysis Implications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Contiguous minute data will represent 1,440 rows of data for a 24hr
period.

Data Calculations
^^^^^^^^^^^^^^^^^^
Calculated fields in addition to those natively from Orchestrator
per-wan-interface include:

#. ``Estimated Kbps``: The average Kbps of Boosted traffic through the
   appliance for the minute based on the Bytes Boosted. This is
   calculated as explained in the introduction by multiplying the bytes
   value by 0.0001333.

    .. code-block:: python

        point.append(point[2] * 0.0001333)

.. warning::

    There is no age out of data in existing csv files already
    collected. Without cleaning up the collection, a large
    amount of data can be collected over time. This example is meant to
    inspire what's possible, not to handle a long-term reporting
    workflow where data may be stored into a database, aged out on a
    retention schedule and other production-quality attributes.

Exported Files
^^^^^^^^^^^^^^^^^

It will create CSV files for each appliance collected in the
``boost_tseries_data`` sub-directory. The files are named in the format
of ``<hostname>_boost_timeseries.csv``.

Example: ``EC-01_boost_timeseries.csv``


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


Running the script to collect data for all appliances:

.. code-block:: bash

    python boost_timeseries.py

Running the script to collect data for single appliance:

.. code-block:: bash

    python boost_timeseries.py -a MY-appliance-01


Orchestrator API calls
^^^^^^^^^^^^^^^^^^^^^^^^^^

The three API calls to Orchestrator (outside of authentication) are:

- :func:`pyedgeconnect.Orchestrator.get_appliances`
- :func:`pyedgeconnect.Orchestrator.get_timeseries_stats_boost_single_appliance`

The ``get_appliances`` function gets all appliances from Orchestrator to
be able to map hostnames with underlying NePK values, as well as
other metadata and state of appliance with Orchestrator.

The ``get_timeseries_stats_boost_single_appliance`` will return
timeseries data for Boost utilization on an appliance.