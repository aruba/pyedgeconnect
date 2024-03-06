import argparse
import getpass
import os
import time
from datetime import datetime

import pandas as pd

from pyedgeconnect import Orchestrator


def collect_data(single_appliance: str = None):
    appliances = orch.get_appliances()

    start_time = int(time.time())
    lookback_time = 86400 * 3  # in seconds, 86400 is 24hrs

    # Limit to single appliance by hostname, if specificed
    if single_appliance is not None:
        selected_appliances = []
        for appliance in appliances:
            if appliance["hostName"] == single_appliance:
                selected_appliances.append(appliance)
    else:
        selected_appliances = appliances

    # Collect timeseries data from appliance if currently reachable by
    # Orchestrator (state == 1)
    for appliance in selected_appliances:
        if appliance["state"] == 1:
            try:
                raw_data = orch.get_timeseries_stats_boost_single_appliance(
                    ne_pk=appliance["id"],
                    start_time=start_time - lookback_time,
                    end_time=start_time,
                    granularity="minute",
                )

                for point in raw_data["data"]:
                    # Convert epoch timestamp to human-readable datetime
                    point[0] = datetime.fromtimestamp(point[0]).strftime(
                        "%m-%d-%Y %H:%M:%S"
                    )

                    # Calculate average Boost utilization
                    # Raw value is Bytes per minute
                    # To estimate Kbps from Bpm raw value
                    # Multiply by 8 to get bits
                    # Divide by 60 to get bits per second
                    # Dvide by 1000 to get kilobits per second
                    # Simplified, multiply the Bytes by 0.0001333

                    # point[5] is the estimated kbps
                    point.append(int(point[2] * 0.0001333))

                    # point[6] is the estimated % utilization
                    # of configured (estimated kpbs / configured kbps)
                    point.append(int(point[5] / point[1]))

                    # point[7] is the appliance hostname
                    point.append(appliance["hostName"])

                filename = f"data/{appliance['hostName']}_boost_timeseries.csv"

                # Create dataframe from data and column headers
                # from newly retrieved data
                df = pd.DataFrame(
                    raw_data["data"],
                    columns=[
                        "Timestamp",
                        "Configured Kbps",
                        "Bytes Boosted",
                        "Seconds Not Boosted",
                        "Boost",
                        "Estimated Kbps",
                        "Estimated Pct Util",
                        "Hostname",
                    ],
                )

                # Set the timestamp as the dataframe index
                df = df.set_index("Timestamp")

                # Write dataframe to CSV
                print(f"writing to csv for {appliance['hostName']}")

                # If there's already a csv for this appliance
                # read in the existing captured data and merge it
                # with the newly collected data, removing duplicate
                # timestamps if there's overlap
                if os.path.isfile(filename):
                    # Read existing CSV file data for appliance into df
                    csv_df = pd.read_csv(filename, header=0, index_col=0)
                    # Concat the retrieved data with the CSV data
                    df = pd.concat([df, csv_df])
                    # Remove duplicate timestamps/index
                    df = df[~df.index.duplicated(keep="first")]
                    # Write the aggregated data to CSV
                    df.to_csv(filename, mode="w", index=True)
                else:
                    df.to_csv(filename)

                max_kbps_ts = df["Estimated Kbps"].idxmax()
                max_kbps = df.loc[
                    df["Estimated Kbps"].idxmax(),
                    "Estimated Kbps",
                ]
                print(
                    f"{appliance['hostName']}: Max Kbps was {max_kbps} at {max_kbps_ts}"  # noqa: W505
                )

            except Exception as e:
                print(f"{e} \n Failed collection from {appliance['hostName']}")

            # Cleanup existing df and pause between appliances
            del df
            time.sleep(5)

        else:
            print(f"{appliance['hostName']} is not currently reachable")


if __name__ == "__main__":
    # Parse runtime arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--orch",
        help="Specify the Orchestrator IP or FQDN",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--appliance",
        help="specify single appliance",
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
    if os.path.exists("data"):
        pass
    else:
        os.makedirs("data")

    # Set arguments
    appliance = vars(args)["appliance"]

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
            print("Authentication to Orchestrator Failed")
            exit()
    # If API key specified, check that key is valid before
    # proceeding
    else:
        confirm_auth = orch.get_orchestrator_hello()
        if confirm_auth != "There was an internal server error.":
            pass
        else:
            print("Authentication to Orchestrator Failed")
            exit()

    # Run the data collection function
    collect_data(appliance)
