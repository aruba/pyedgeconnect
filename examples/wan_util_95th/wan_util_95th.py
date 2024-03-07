import argparse
import getpass
import json
import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pandas as pd
import pytz
from timezonefinder import TimezoneFinder

from pyedgeconnect import Orchestrator

# Business days/hours filtering
BUSINESS_HOURS_START = "09:00"  # 09:00 = 9am
BUSINESS_HOURS_END = "17:00"  # 17:00 = 5pm
BUSINESS_DAY_START = 0  # 0 is Monday, logic is >= start day
BUSINESS_DAY_END = 4  # 7 is Sunday, logic is <= end day

# Data collection parameters
# Fixed minute-data retention in OaaS
# Default in on-premises Orchestrator
LOOKBACK_DAYS = 3

# Seconds between appliance data collection
COLLECTION_SLEEP_BETWEEN_APPLIANCES = 5

# Export filenames and directories
DATA_FOLDER = "data/wan_int_tseries_data"
REPORT_FOLDER = "data/wan_int_tseries_reports"
LOG_FOLDER = "data/logging"
APPLIANCE_INT_COMMENT_FILE = "appliance_interface_comments.json"

# System aggregate titles
SYS_DEP_OUT_TITLE = "Sys Agg vs Deployment Outbound"
SYS_DEP_IN_TITLE = "Sys Agg vs Deployment Inbound"
SYS_LIC_OUT_TITLE = "Sys Agg vs License Outbound"
SYS_LIC_IN_TITLE = "Sys Agg vs License Inbound"
SYSTEM_VALUE_COLUMNS = [
    SYS_LIC_OUT_TITLE,
    SYS_LIC_IN_TITLE,
    SYS_DEP_OUT_TITLE,
    SYS_DEP_IN_TITLE,
]


# Timer class to track processing time within a collection task
class Timer:
    def __init__(self):
        self._start_time = None
        self._elapsed_time = None

    def start(self):
        """Start a new timer"""
        self._start_time = time.perf_counter()

    def current(self):
        """Calculate current running time on timer"""
        current_time = time.perf_counter() - self._start_time
        return f"{current_time:0.2f}"

    def stop(self):
        """Stop the timer"""
        self._start_time = None


def collect_data(  # noqa: C901
    single_appliance: str = None, only_deployment: bool = False
):
    appliances = orch.get_appliances()

    # Get all EdgeConnect appliance locations from Orchestrator
    ec_locations = orch.get_all_appliance_locations()
    # Capture lat/long coordinates to determine timezone
    # This won't account for daylight savings time offsets
    ec_location_dict = {}
    for ec_location in ec_locations:
        # Only log locations of appliances
        if ec_location["appliance"] is True:
            ec_location_dict[ec_location["sourceId"]] = {
                "latitude": ec_location["latitude"],
                "longitude": ec_location["longitude"],
            }
        else:
            pass

    # Instantiate timezonefinder for determining timezone for appliance
    tzf = TimezoneFinder()

    start_time = int(time.time())
    lookback_time = 86400 * LOOKBACK_DAYS  # in seconds, 86400 is 24hrs

    # Limit to single appliance by hostname, if specificed
    if single_appliance is not None:
        selected_appliances = []
        for appliance in appliances:
            if appliance["hostName"] == single_appliance:
                selected_appliances.append(appliance)
    else:
        selected_appliances = appliances

    appliance_int_comments = []

    # Collect timeseries data from appliance if currently reachable by
    # Orchestrator (state == 1)
    appliance_count = 0
    for appliance in selected_appliances:
        if appliance["state"] == 1:
            logger.debug(
                f"Collecting data for {appliance['hostName']}, {appliance_count} appliances reviewed in total"
            )
            # Get appliance deployment
            deployment = orch.get_appliance_deployment(appliance["id"])

            # Determine timezone by appliance lat/long coordinates
            # Calculates utc offset per-appliance based on timezone
            timezone_str = tzf.timezone_at(
                lat=ec_location_dict[appliance["id"]]["latitude"],
                lng=ec_location_dict[appliance["id"]]["longitude"],
            )
            timezone = pytz.timezone(timezone_str)

            # If deployment values not returned, skip details
            if type(deployment) is bool:
                logger.error(
                    f"Could not retrieve deployment for {appliance['hostName']}"
                )
            else:
                # Appliance license
                license_value = int(
                    deployment["sysConfig"]["license"]["ecTierBW"]
                )
                # Appliance max deployment values
                deployment_max_outbound = deployment["sysConfig"]["maxBW"]
                # total inbound bandwidth
                deployment_max_inbound = deployment["sysConfig"]["maxInBW"]

                # Map WAN labels into flat dictionary for easier lookup
                wan_labels = {}
                for labelmap in deployment["sysConfig"]["ifLabels"]["wan"]:
                    wan_labels[labelmap["id"]] = labelmap["name"]

                # Assemble list of in-use WAN interfaces
                wan_interfaces = {}

                # Parse appliance interfaces for WAN interfaces that
                # are in use
                for interface in deployment["modeIfs"]:
                    # Loop over all ip interfaces per-interface
                    for ip_int in interface["applianceIPs"]:
                        # If interrface is configured for WAN use and
                        # has label applied
                        if ip_int["wanSide"] is True and ip_int["label"] != "":
                            # If interface has vlan tagging, capture
                            # full interface name with tag
                            if ip_int.get("vlan") is not None:
                                int_name = (
                                    f"{interface['ifName']}.{ip_int['vlan']}"
                                )
                            else:
                                int_name = interface["ifName"]
                            # Capture interface WAN label and comment
                            wan_interfaces[int_name] = {}
                            wan_interfaces[int_name]["label"] = wan_labels[
                                ip_int["label"]
                            ]
                            wan_interfaces[int_name]["comment"] = ip_int[
                                "comment"
                            ]

            # To be added to appliance interface comment mapping
            appliance_dict = {"Appliance": appliance["hostName"]}
            for wan_int in wan_interfaces:
                try:
                    appliance_dict[wan_interfaces[wan_int]["label"]] = (
                        wan_interfaces[wan_int]["comment"]
                    )

                    # If set to only collect deployment mapping, skip
                    # timeseries collection
                    if only_deployment:
                        pass
                    else:
                        logger.debug(
                            f"Collecting time series for {appliance['hostName']}:{wan_int}"
                        )
                        try:
                            raw_data = orch.get_timeseries_stats_interface_single_appliance(
                                ne_pk=appliance["id"],
                                start_time=start_time - lookback_time,
                                end_time=start_time,
                                granularity="minute",
                                traffic_type="all_traffic",
                                interface_name=wan_int,
                            )
                        except Exception as e:
                            logger.error(e)
                            logger.error(
                                f"ERROR: Could not retrieve timeseries for {appliance['hostName']}:{wan_int} between {start_time}--{lookback_time}"
                            )

                        if len(raw_data) > 0:
                            logger.debug(
                                f"Successfully retrieved data from {appliance['hostName']}:{wan_int}"
                            )
                            # Calculate timestamp into local timezone
                            # time and weekday
                            # Calculate offset once, then convert all
                            # times
                            utc_offset = timezone.utcoffset(
                                datetime.fromtimestamp(
                                    raw_data[0]["timestamp"]
                                )
                            )
                            for point in raw_data:
                                # Local time in column tz_time
                                # calculated from UTC time + offset
                                point["tz_time"] = (
                                    datetime.utcfromtimestamp(
                                        point["timestamp"]
                                    )
                                    + utc_offset
                                ).strftime("%m-%d-%Y%H:%M:%S")

                                # Calculate average percentage
                                # utilization vs deployment values
                                # total bytes * 8 / 60 for bits/second
                                # Divided by deployment (in kpbs) * 1000
                                # for a bytes/bytes comparison
                                # Multiplied by 100 for 0-100
                                # percent values
                                try:
                                    point["pct_outbound"] = (
                                        ((point["tx_bytes"] * 8) / 60)
                                        / (point["max_bw_tx"] * 1000)
                                    ) * 100
                                    point["pct_inbound"] = (
                                        ((point["rx_bytes"] * 8) / 60)
                                        / (point["max_bw_rx"] * 1000)
                                    ) * 100
                                except Exception as e:
                                    logger.error(e)
                                    logger.error(
                                        "Could not calculate percentage utilization against deployment values"
                                    )
                                    logger.error(
                                        f"{appliance['hostName']}:{point['interfaceName']} @ {point['tz_time']} - tx:{point['tx_bytes']} deptx:{point['max_bw_tx']} rx:{point['rx_bytes']} deprx:{point['max_bw_rx']}"
                                    )

                                point["label"] = wan_interfaces[wan_int][
                                    "label"
                                ]
                                point["license"] = license_value
                                point["system_max_outbound"] = (
                                    deployment_max_outbound
                                )
                                point["system_max_inbound"] = (
                                    deployment_max_inbound
                                )
                                point["hostname"] = appliance["hostName"]
                                point["site"] = appliance["site"]
                                point["int_comment"] = wan_interfaces[wan_int][
                                    "comment"
                                ]

                            # Drop unnecessary columns from raw
                            # response data
                            # e.g. overhead bytes, firewall drop
                            # counts, etc.
                            df = pd.DataFrame(raw_data)
                            df = df[
                                [
                                    "tz_time",
                                    "timestamp",
                                    "hostname",
                                    "site",
                                    "license",
                                    "interfaceName",
                                    "label",
                                    "int_comment",
                                    "tx_bytes",
                                    "rx_bytes",
                                    "tx_bytes_max",
                                    "tx_bytes_max_ts",
                                    "rx_bytes_max",
                                    "rx_bytes_max_ts",
                                    "max_bw_tx",
                                    "max_bw_rx",
                                    "pct_outbound",
                                    "pct_inbound",
                                    "system_max_outbound",
                                    "system_max_inbound",
                                ]
                            ]

                            # Convert local timezone timestamp to
                            # dataframe index
                            df["datetime"] = pd.to_datetime(
                                df["tz_time"], format="%m-%d-%Y%H:%M:%S"
                            )
                            df = df.set_index("datetime")

                            logger.debug(
                                f"writing to csv for {appliance['hostName']}:{wan_int}"
                            )

                            filename = f"{DATA_FOLDER}/{appliance['hostName']}__{wan_int}_{wan_interfaces[wan_int]['label']}.csv"

                            # If there's already a csv for this
                            # appliance read in the existing captured
                            # data and merge it with the newly collected
                            # data, removing duplicate timestamps if
                            # there's overlap
                            if os.path.isfile(filename):
                                # Read existing CSV file data for
                                # appliance into df
                                csv_df = pd.read_csv(
                                    filename, header=0, index_col=0
                                )
                                # Concat the retrieved data with
                                # the CSV data
                                df = pd.concat([df, csv_df])
                                # Remove duplicate timestamps/index
                                df = df[~df.index.duplicated(keep="first")]
                                # Write the aggregated data to CSV
                                df.to_csv(filename, mode="w", index=True)
                            else:
                                df.to_csv(filename)

                        else:
                            logger.error(
                                f"No data retrieved for {appliance['hostName']}:{wan_int}"  # noqa: W505
                            )
                except Exception as e:
                    logger.error(e)
                    logger.error(
                        f"Could not complete data collection for {appliance['hostName']}:{wan_int}"
                    )

            # Append appliance metadata for label/comment mapping
            appliance_int_comments.append(appliance_dict)
            # Cleanup existing df from memory
            # Pause between appliances to avoid overwhelming
            # Orchestrator with API calls
            del df
            time.sleep(COLLECTION_SLEEP_BETWEEN_APPLIANCES)

        else:
            logger.error(
                f"{appliance['hostName']} is not currently reachable for data retrieval"
            )
        appliance_count += 1
    # If the file already exists, read in contents
    # update existing appliances, append new data
    if os.path.isfile(f"{DATA_FOLDER}/{APPLIANCE_INT_COMMENT_FILE}"):
        # open file to read in existing data
        with open(f"{DATA_FOLDER}/{APPLIANCE_INT_COMMENT_FILE}", "r") as jfile:
            existing_app_int_comments = json.load(jfile)

        # List of new appliances
        new_appliances = []
        for new_appliance in appliance_int_comments:
            new_appliances.append(new_appliance["Appliance"])
        # Add existing appliances absent from newly collected
        # If appliance was in existing file and newly collected
        # the new values will be used
        for existing_appliance in existing_app_int_comments:
            if existing_appliance["Appliance"] not in new_appliances:
                appliance_int_comments.append(existing_appliance)

    # reopen file as write with all data
    # Write collected configuration data out to file
    with open(f"{DATA_FOLDER}/{APPLIANCE_INT_COMMENT_FILE}", "w") as jfile:
        json.dump(appliance_int_comments, jfile)

    logger.critical(
        f"{proc_timer.current()}: --------COLLECTION COMPLETE--------"
    )
    proc_timer.stop()


def analyze_data(single_appliance: str = None):  # noqa: C901
    # Tracking total datapoints read in and processed
    data_points_processed = 0
    data_points_read = 0

    appliance_report_list = []

    # Create list of dataframes for each csv file in the data
    # collection folder
    csvfilelist = []
    for file in os.listdir(DATA_FOLDER):
        # Only read in files for single appliance if specified
        if single_appliance is not None:
            if file.endswith(".csv") and single_appliance in file:
                csvfilelist.append(file)
        else:
            if file.endswith(".csv"):
                csvfilelist.append(file)

    # Raise exception if no files found to process
    if len(csvfilelist) == 0:
        message = f"No files in {DATA_FOLDER} to process"
        logger.error(message)
        raise FileNotFoundError(message)

    logger.debug(f"{proc_timer.current()}: Reading CSVs to DFs")

    all_csv_df_list = [
        pd.read_csv(f"{DATA_FOLDER}/{csvfile}") for csvfile in csvfilelist
    ]

    logger.debug(f"{proc_timer.current()}: Completed CSVs to DFs")

    # Limit to single appliance by hostname, if specificed
    all_df_list = []
    for df in all_csv_df_list:
        if single_appliance is not None:
            if df["hostname"].unique()[0] == single_appliance:
                all_df_list.append(df)
        else:
            all_df_list = list(all_csv_df_list)

    # Read in Appliance / Interface / Comment mapping
    with open(f"{DATA_FOLDER}/{APPLIANCE_INT_COMMENT_FILE}", "r") as jfile:
        appliance_int_comment_map = json.load(jfile)
    appliance_int_comment_df = pd.DataFrame(appliance_int_comment_map)

    # Identify all unique appliances across ingested csv files
    unique_appliances = []
    for df in all_df_list:
        if df["hostname"].unique()[0] not in unique_appliances:
            unique_appliances.append(df["hostname"].unique()[0])

    # Create list of df's for one appliance
    interface_appliance_df_list = []

    logger.debug(
        f"{proc_timer.current()}: Begin filtering hours/days from dataset"
    )

    for appliance in unique_appliances:
        # Counter for multiple df's of a single appliance
        app_df_counter = 0
        temp_appliance_df_list = []
        for df in all_df_list:
            if df["hostname"].unique()[0] == appliance:
                app_df_counter += 1
                data_points_read += len(df) * len(df.columns)

                logger.debug(
                    f"{proc_timer.current()}: Begin filtering hours/days from dataset {appliance} df#{app_df_counter}"
                )

                # Set index on datetime field
                # Convert local timezone timestamp to dataframe index
                df["datetime"] = pd.to_datetime(
                    df["tz_time"], format="%m-%d-%Y%H:%M:%S"
                )
                df = df.set_index("datetime")

                # Drop non-business hours
                df = df.between_time(
                    BUSINESS_HOURS_START,
                    BUSINESS_HOURS_END,
                )

                # Drop non-business days
                # < 5 is equivalent to Mon-Fri where Friday is 4
                df = df[
                    (df.index.dayofweek >= BUSINESS_DAY_START)
                    & (df.index.dayofweek <= BUSINESS_DAY_END)
                ]

                # Skip if filtering days/hours has removed all points
                if len(df) == 0:
                    pass
                else:
                    # Append list for each appliance df to merge
                    # if df["hostname"].unique()[0] == appliance:
                    temp_appliance_df_list.append(df)

        # Skip if filtering days/hours has removed all points for
        # appliance
        if len(temp_appliance_df_list) == 0:
            pass
        else:
            # Merge all df for single appliance into one df
            appliance_df = pd.concat(temp_appliance_df_list)
            # Remove duplicate timestamps for same label from the
            # combined df
            appliance_df = appliance_df.drop_duplicates(
                subset=["timestamp", "label"]
            )
            # Append to merged appliance df list
            interface_appliance_df_list.append(appliance_df)

    logger.info(
        f"{proc_timer.current()}: Filtering hours/days from dataset Completed"
    )
    total_labels = 0
    # Calculate analytics and insert into report df
    for df in interface_appliance_df_list:
        logger.debug(
            f"{proc_timer.current()}: Calculating per-label 95ths for {df['hostname'].iloc[0]}"
        )

        data_points_processed += len(df) * len(df.columns)

        labels = df.label.unique()

        # Calculate 95 percentiles of percent utilization against
        # deployment for inbound/outbound for each label
        label_analytics = {}
        for label in labels:
            total_labels += 1
            # Filter for current label
            label_df = df[df.label == label]
            # Calculate 95th percentile utilization
            label_analytics[f"{label} inbound"] = round(
                label_df.pct_inbound.quantile(0.95), 2
            )
            label_analytics[f"{label} outbound"] = round(
                label_df.pct_outbound.quantile(0.95), 2
            )

        logger.debug(
            f"{proc_timer.current()}: Calculating system 95ths for {df['hostname'].iloc[0]}"
        )

        # Calculate system utilziation percentages
        # For matching timestamps, sum all WAN interfaces for RX bytes
        # and TX bytes
        system_df = (
            df.groupby(
                [
                    "timestamp",
                    "system_max_inbound",
                    "system_max_outbound",
                    "license",
                ]
            )[["rx_bytes", "tx_bytes"]]
            .sum()
            .reset_index()
        )

        logger.debug(
            f"{proc_timer.current()}: Calculating system in/out 95ths for {df['hostname'].iloc[0]}"
        )

        # Calculate system percentage utilizations
        system_df["system_dep_pct_inbound"] = round(
            (
                (system_df["rx_bytes"] * 8 / 60)
                / (system_df["system_max_inbound"] * 1000)
            )
            * 100,
            2,
        )
        system_df["system_dep_pct_outbound"] = round(
            (
                (system_df["tx_bytes"] * 8 / 60)
                / (system_df["system_max_outbound"] * 1000)
            )
            * 100,
            2,
        )
        system_df["system_lic_pct_inbound"] = round(
            ((system_df["rx_bytes"] * 8 / 60) / (system_df["license"] * 1000))
            * 100,
            2,
        )
        system_df["system_lic_pct_outbound"] = round(
            ((system_df["tx_bytes"] * 8 / 60) / (system_df["license"] * 1000))
            * 100,
            2,
        )

        logger.debug(
            f"{proc_timer.current()}: Add license type/values for {df['hostname'].iloc[0]}"
        )

        # Add license type for reporting
        # Don't calculate % utilization on Unlimited licenses
        license_kpbs = df["license"].iloc[0]
        if license_kpbs == 1000000000:
            license_value = "Unlimited"
            lic_95th_in = "N/A"
            lic_95th_out = "N/A"
        # Calculate friendly Gbps or Mbps representation of
        # license value
        elif license_kpbs > 0:
            if license_kpbs > 500000:
                license_value = f"{int(license_kpbs/1000/1000)}G"
            else:
                license_value = f"{int(license_kpbs/1000)}M"
            # Calculate utilization against license value if not
            # Unlimited
            lic_95th_in = round(
                system_df.system_lic_pct_inbound.quantile(0.95), 2
            )
            lic_95th_out = round(
                system_df.system_lic_pct_outbound.quantile(0.95), 2
            )
        # If license value requested doesn't match license granted by
        # Orchestrator the retrieved value will be 0
        else:
            lic_95th_in = "N/A"
            lic_95th_out = "N/A"

        logger.debug(
            f"{proc_timer.current()}: Finalize system values for {df['hostname'].iloc[0]}"
        )

        # Calculate system-wide 95th percentiles from new calculated
        # values above
        system_wide = {
            "Appliance": df["hostname"].iloc[0],
            "Site": df["site"].iloc[0],
            "License": license_value,
            SYS_DEP_IN_TITLE: round(
                system_df.system_dep_pct_inbound.quantile(0.95), 2
            ),
            SYS_DEP_OUT_TITLE: round(
                system_df.system_dep_pct_outbound.quantile(0.95), 2
            ),
            SYS_LIC_IN_TITLE: lic_95th_in,
            SYS_LIC_OUT_TITLE: lic_95th_out,
        }

        logger.debug(
            f"{proc_timer.current()}: Merge system data dict for {df['hostname'].iloc[0]}"
        )

        # Merge system stats with per-label stats into single dictionary
        appliance_analytics = {**system_wide, **label_analytics}
        appliance_report_list.append(appliance_analytics)

    logger.info(f"{proc_timer.current()}: Saving data to export CSVs")

    # Add all appliance stats dictionaries into a dataframe
    df = pd.DataFrame.from_records(appliance_report_list)
    logger.info(f"TOTAL DATAPOINTS READ: {data_points_read}")
    logger.info(f"TOTAL DATAPOINTS PROCESSED: {data_points_processed}")
    logger.info(f"TOTAL WAN INTERFACES PROCESSED: {total_labels}")

    # Export result to csv
    report_timestamp = datetime.fromtimestamp(int(time.time())).strftime(
        "%Y-%m-%d_%H_%M_%S"
    )

    # Visualization of DataFrames into Tables and Graphs
    logger.debug(f"{proc_timer.current()}: Creating HTML table figures")

    # System Aggregate Utiilzation Table
    meta_columns = [
        "Appliance",
        "Site",
        "License",
    ]

    system_stats_columns = meta_columns.copy()
    system_stats_columns.extend(SYSTEM_VALUE_COLUMNS)

    # Sort system aggregate table by utilization in order compared to
    # license value outbound
    # license value inbound
    # deployment value outbound
    # deployment value inbound
    df = df.sort_values(
        SYSTEM_VALUE_COLUMNS,
        ascending=False,
    )

    # Drop per-label values for generating system level table
    system_stats_df = df[system_stats_columns]
    logger.info(f"Appliances in analysis: {len(system_stats_df)}")
    logger.info(f"WAN interfaces in analysis: {total_labels}")

    # Merging per-label utilization data with per-label comments from
    # appliances
    # Index both on "Appliance" value
    appliance_df = df.set_index("Appliance")
    appliance_int_comment_df = appliance_int_comment_df.set_index("Appliance")
    # Export fully merged table of system values,
    # per-label values, and interface comments
    master_export_df = appliance_df.join(appliance_int_comment_df)

    # Take all label-related column names to be sorted
    # Not including "Appliance" or "Site"
    master_export_df_columns = list(master_export_df.columns)
    non_sorted_columns = [
        "Site",
        "License",
        SYS_LIC_OUT_TITLE,
        SYS_LIC_IN_TITLE,
        SYS_DEP_OUT_TITLE,
        SYS_DEP_IN_TITLE,
    ]
    for column in non_sorted_columns:
        master_export_df_columns.remove(column)
    sorted_master_columns = sorted(master_export_df_columns)
    # Add "Site","License" back to column names
    master_label_list = non_sorted_columns.copy()
    master_label_list.extend(sorted_master_columns)
    # Reindex DataFrame with sorted columns and reset index to bring
    # "Appliance" column back
    master_export_df = master_export_df.reindex(master_label_list, axis=1)
    master_export_df.reset_index(inplace=True)

    master_export_df.to_csv(
        f"{REPORT_FOLDER}/{report_timestamp}_report_dataframe.csv", index=False
    )

    logger.critical(
        f"{proc_timer.current()}: --------ANALYSIS COMPLETE--------"
    )
    proc_timer.stop()


if __name__ == "__main__":  # noqa: C901
    # Parse runtime arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--orch",
        help="Specify the Orchestrator IP or FQDN",
        type=str,
    )
    parser.add_argument(
        "-c",
        "--collect",
        help="Collect data for analysis",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-d",
        "--deployment",
        help="Only collect deployment mapping",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-r",
        "--report",
        help="Report on data",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-a",
        "--appliance",
        help="specify single appliance",
        type=str,
    )
    parser.add_argument(
        "-ll",
        "--loglevel",
        help="specify logging level, e.g. INFO",
        type=str,
    )
    args = parser.parse_args()

    # Set Orchestrator FQDN/IP via arguments, environment variable,
    # or user input if neither in argument or environment variable
    if vars(args)["orch"] is not None:
        orch_url = vars(args)["orch"]
    elif os.getenv("ORCH_URL") is not None:
        orch_url = os.getenv("ORCH_URL")
    else:
        orch_url = input("Orchstrator IP or FQDN: ")

    # Instantiate data collection and report folders
    # if they don't already exist
    if os.path.exists(DATA_FOLDER):
        pass
    else:
        os.makedirs(DATA_FOLDER)

    if os.path.exists(REPORT_FOLDER):
        pass
    else:
        os.makedirs(REPORT_FOLDER)

    # Set arguments
    collect = vars(args)["collect"]
    only_deployment = vars(args)["deployment"]
    report = vars(args)["report"]
    appliance = vars(args)["appliance"]
    log_level = vars(args)["loglevel"]

    # Setup log settings for messages and errors
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    log_file_handler = RotatingFileHandler(
        f"{LOG_FOLDER}/pyedgeconnect95th.log",
        maxBytes=100000,
        backupCount=5,
    )
    log_file_handler.setFormatter(formatter)
    if log_level == "CRITICAL":
        logger.setLevel(logging.CRTICAL)
    elif log_level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif log_level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif log_level == "INFO":
        logger.setLevel(logging.INFO)
    elif log_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.disabled = True
    logger.addHandler(log_file_handler)

    # Start timing process
    proc_timer = Timer()
    proc_timer.start()

    if collect:
        logger.critical(
            f"{proc_timer.current()}: --------COLLECTION STARTED--------"
        )
        logger.critical(f"{proc_timer.current()}: {orch_url}")
        # Set Orchestrator API Key via environment variable or user
        # input
        # Skipping will fallback to user/password authentication
        if os.getenv("ORCH_API_KEY") is not None:
            orch_api_key = os.getenv("ORCH_API_KEY")
        else:
            orch_api_key_input = getpass.getpass(
                "Orchstrator API Key (enter to skip): "
            )
            if len(orch_api_key_input) == 0:
                orch_api_key = None
                # Set user and password if present in environment
                # variable
                orch_user = os.getenv("ORCH_USER")
                orch_pw = os.getenv("ORCH_PASSWORD")
            else:
                orch_api_key = orch_api_key_input

        # Instantiate Orchestrator with ``log_console`` enabled for
        # printing log messages to terminal, and ``verify_ssl`` to False
        # which will not verify the web https certificate on
        # Orchestrator

        orch = Orchestrator(
            orch_url,
            api_key=orch_api_key,
            log_console=True,
            verify_ssl=False,
        )

        # If not using API key, login to Orchestrator with
        # username/password
        if orch_api_key is None:
            # If username/password not in environment variables,
            # prompt user
            if orch_user is None:
                orch_user = input("Enter Orchestrator username: ")
                orch_pw = getpass.getpass("Enter Orchestrator password: ")
            # Check if multi-factor authentication required
            mfa_prompt = input("Are you using MFA for this user (y/n)?: ")
            if mfa_prompt == "y":
                orch.send_mfa(orch_user, orch_pw, temp_code=False)
                token = input("Enter MFA token: ")
            else:
                token = ""
            # Login to Orchestrator with user/password to check auth
            # before proceeding
            confirm_auth = orch.login(orch_user, orch_pw, mfacode=token)
            if confirm_auth:
                pass
            else:
                message = "Authentication to Orchestrator Failed"
                print(message)
                logger.error(message)
                exit()
        # If API key specified, check that key is valid before
        # proceeding
        else:
            confirm_auth = orch.get_orchestrator_hello()
            if confirm_auth != "There was an internal server error.":
                pass
            else:
                message = "Authentication to Orchestrator Failed"
                print(message)
                logger.error(message)
                exit()

        # Run the data collection function
        collect_data(appliance, only_deployment)

    if report:
        logger.critical(
            f"{proc_timer.current()}: --------REPORT STARTED--------"
        )
        logger.critical(f"{proc_timer.current()}: {orch_url}")
        analyze_data(appliance)
