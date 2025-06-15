"""Script for transforming extracted data from RDS into PDF summary report."""

import datetime

import pandas as pd
from pandas import DataFrame


def get_pct_trains_dep_delayed_five_mins(station_data: list[dict]) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""

    station_data = DataFrame(station_data)


def get_pct_trains_arr_delayed_five_mins(station_data: list[dict]) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""
    ...


def get_pct_trains_cancelled(station_data: list[dict]) -> float:
    """Gets the percentage of trains cancelled."""
    ...


def get_avg_dep_delay_all_trains(station_data: list[dict]) -> float:
    """Gets the average departure delay of all trains."""
    ...


def get_avg_arr_delay_all_trains(station_data: list[dict]) -> float:
    """Gets the average arrival delay of all trains."""
    ...


def get_avg_dep_delay_delayed_trains(station_data: list[dict]) -> float:
    """Gets the average departure delay of trains delayed at least one minute."""
    ...


def get_avg_arr_delay_delayed_trains(station_data: list[dict]) -> float:
    """Gets the average arrival delay of trains delayed at least one minute."""
    ...


if __name__ == "__main__":
    ...
