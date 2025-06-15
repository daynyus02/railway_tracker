"""Script for transforming extracted data from RDS into PDF summary report."""

import datetime as dt

import pandas as pd
from pandas import DataFrame


def convert_train_times_to_date_times(data: DataFrame) -> DataFrame:
    """Convert time columns to datetime objects to allow maths operations."""

    train_date = data.loc[0, "service_date"]

    time_columns = ["scheduled_arr_time", "actual_arr_time",
                    "scheduled_dep_time", "actual_dep_time"]

    for column in time_columns:
        data[column] = data[column].apply(
            lambda t: dt.datetime.combine(train_date, t))

    return data


def get_pct_trains_dep_delayed_five_mins(data: DataFrame) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""

    data = convert_train_times_to_date_times(data)

    delayed_trains = len(data[data["actual_dep_time"] >
                         data["scheduled_dep_time"]+dt.timedelta(minutes=5)])

    return delayed_trains/len(data) * 100


def get_pct_trains_arr_delayed_five_mins(data: DataFrame) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""

    data = convert_train_times_to_date_times(data)

    delayed_trains = len(data[data["actual_arr_time"] >
                              data["scheduled_arr_time"]+dt.timedelta(minutes=5)])

    return delayed_trains/len(data) * 100


def get_pct_trains_cancelled(data: DataFrame) -> float:
    """Gets the percentage of trains cancelled."""

    cancelled_trains = int(data["cancellation_id"].count())

    return cancelled_trains/len(data) * 100


def get_avg_dep_delay_all_trains(data: DataFrame) -> float:
    """Gets the average departure delay of all trains."""


def get_avg_arr_delay_all_trains(data: DataFrame) -> float:
    """Gets the average arrival delay of all trains."""
    ...


def get_avg_dep_delay_delayed_trains(data: DataFrame) -> float:
    """Gets the average departure delay of trains delayed at least one minute."""
    ...


def get_avg_arr_delay_delayed_trains(data: DataFrame) -> float:
    """Gets the average arrival delay of trains delayed at least one minute."""
    ...


if __name__ == "__main__":
    ...
