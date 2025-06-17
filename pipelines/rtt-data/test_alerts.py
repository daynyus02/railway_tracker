"""Test for alert functions that send alerts/notifications to a user."""
# pylint: skip-file

from pandas import DataFrame
from datetime import time
from alerts import get_delayed_trains


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
