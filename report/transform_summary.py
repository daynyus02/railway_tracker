"""Script for transforming extracted data from RDS into PDF summary report."""

import datetime as dt

from pandas import DataFrame
import pandas as pd


def convert_train_times_to_date_times(data: DataFrame) -> DataFrame:
    """Convert time columns to datetime objects to allow maths operations."""
    train_date = data.loc[0, "service_date"]

    time_columns = ["scheduled_arr_time", "actual_arr_time",
                    "scheduled_dep_time", "actual_dep_time"]

    for column in time_columns:
        data[column] = data[column].apply(
            lambda t: (dt.datetime.combine(train_date, t.time()if isinstance(
                t, dt.datetime) else t) if pd.notna(t) else pd.NaT)
        )

    return data


def convert_timedelta_to_str(td: dt.timedelta) -> str:
    """Converts timedelta object to string in %H:%M:%S format."""

    total_seconds = td.total_seconds() % 86400

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    if td.days > 0:
        return str(td).replace(",", "")

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def get_pct_trains_dep_delayed_five_mins(data: DataFrame) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""

    data = convert_train_times_to_date_times(data)

    delayed_trains = len(data[data["actual_dep_time"] >=
                         data["scheduled_dep_time"]+dt.timedelta(minutes=5)])

    return delayed_trains/len(data) * 100


def get_pct_trains_arr_delayed_five_mins(data: DataFrame) -> float:
    """Gets the percentage of trains with departure delayed by five or more minutes."""

    data = convert_train_times_to_date_times(data)

    delayed_trains = len(data[data["actual_arr_time"] >=
                              data["scheduled_arr_time"]+dt.timedelta(minutes=5)])

    return delayed_trains/len(data) * 100


def get_pct_trains_cancelled(data: DataFrame) -> float:
    """Gets the percentage of trains cancelled."""

    cancelled_trains = int(data["cancellation_id"].count())

    return cancelled_trains/len(data) * 100


def get_avg_dep_delay_all_trains(data: DataFrame) -> str:
    """Gets the average departure delay of all trains as %H:%M:%S string."""

    data = convert_train_times_to_date_times(data)

    data['dep_delay'] = data["actual_dep_time"] - data["scheduled_dep_time"]
    delayed_trains = data[data['dep_delay'] > dt.timedelta(0, 0)]

    total_delays = sum(delayed_trains['dep_delay'], dt.timedelta())

    avg_delay = total_delays/len(data)

    return convert_timedelta_to_str(avg_delay)


def get_avg_arr_delay_all_trains(data: DataFrame) -> str:
    """Gets the average arrival delay of all trains as %H:%M:%S string."""

    data = convert_train_times_to_date_times(data)

    data['arr_delay'] = data["actual_arr_time"] - data["scheduled_arr_time"]
    delayed_trains = data[data['arr_delay'] > dt.timedelta(0, 0)]

    total_delays = sum(delayed_trains['arr_delay'], dt.timedelta())

    avg_delay = total_delays/len(data)

    return convert_timedelta_to_str(avg_delay)


def get_avg_dep_delay_delayed_trains(data: DataFrame) -> str:
    """Gets the average departure delay of trains delayed at least one minute as %H:%M:%S string."""

    data = convert_train_times_to_date_times(data)

    data['dep_delay'] = data["actual_dep_time"] - data["scheduled_dep_time"]
    delayed_trains = data[data['dep_delay'] > dt.timedelta(0, 0)]

    total_delays = sum(delayed_trains['dep_delay'], dt.timedelta())

    avg_delay = total_delays/len(delayed_trains)

    return convert_timedelta_to_str(avg_delay)


def get_avg_arr_delay_delayed_trains(data: DataFrame) -> str:
    """Gets the average arrival delay of trains delayed at least one minute as %H:%M:%S string."""

    data = convert_train_times_to_date_times(data)

    data['arr_delay'] = data["actual_arr_time"] - data["scheduled_arr_time"]
    delayed_trains = data[data['arr_delay'] > dt.timedelta(0, 0)]

    total_delays = sum(delayed_trains['arr_delay'], dt.timedelta())

    avg_delay = total_delays/len(delayed_trains)

    return convert_timedelta_to_str(avg_delay)


def get_station_summary(data: DataFrame) -> dict:
    """Returns a dictionary for summary statistics for a train station."""

    return {
        "% trains departing delayed by 5+ minutes": get_pct_trains_dep_delayed_five_mins(data),
        "% trains arriving delayed by 5+ minutes": get_pct_trains_arr_delayed_five_mins(data),
        "% trains cancelled": get_pct_trains_cancelled(data),
        "Average departure delay (all trains)": get_avg_dep_delay_all_trains(data),
        "Average arrival delay (all trains)": get_avg_arr_delay_all_trains(data),
        "Average departure delay (delayed trains)": get_avg_dep_delay_delayed_trains(data),
        "Average arrival delay (delayed trains)": get_avg_arr_delay_delayed_trains(data),
    }
