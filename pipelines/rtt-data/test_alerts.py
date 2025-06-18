"""Test for alert functions that send alerts/notifications to a user."""
# pylint: skip-file
from alerts import send_notification
import logging
import pandas as pd
from pandas import DataFrame
from datetime import time
from unittest.mock import patch, MagicMock
from alerts import get_delayed_trains, filter_by_route, send_notification


def test_get_delayed_trains():
    test_data = {
        "scheduled_dep_time": [time(14, 0), time(15, 0), time(16, 0), None],
        "actual_dep_time": [time(14, 5), time(15, 0), time(15, 55), time(16, 10)]
    }

    test_df = DataFrame(test_data)

    delayed_trains = get_delayed_trains(test_df)

    assert len(delayed_trains) == 1
    assert delayed_trains.iloc[0]["scheduled_dep_time"] == time(14, 0)
    assert delayed_trains.iloc[0]["actual_dep_time"] == time(14, 5)


def test_filter_by_route():
    test_data = {
        "origin_name":
            ["London Paddington", "London Paddington",
                "Edinburgh", "London Paddington"],
        "destination_name": [
            "Bristol Temple Meads", "Oxford", "Bristol Temple Meads", "Bristol Temple Meads"
        ],
    }

    test_df = DataFrame(test_data)

    result = filter_by_route(
        test_df, "London Paddington", "Bristol Temple Meads")
    assert len(result) == 2

    result = filter_by_route(test_df, "Leeds", "Bristol Temple Meads")
    assert result.empty

    result = filter_by_route(test_df, "Edinburgh", "Bristol Temple Meads")
    assert len(result) == 1
