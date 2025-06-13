# pylint: skip-file
"""Fixture that is used within the test_transform.py"""

import pytest
from pandas import DataFrame


@pytest.fixture
def test_data():
    return DataFrame([{
        "service_uid": "abc123",
        "train_identity": "1A01",
        "station_name": "Paddington",
        "station_crs": "PAD",
        "origin_name": "Reading",
        "destination_name": "Oxford",
        "scheduled_arr_time": "1230",
        "actual_arr_time": "1245",
        "scheduled_dep_time": "1250",
        "actual_dep_time": "1300",
        "operator_name": "GWR",
        "service_date": "2024-05-01",
        "platform": "2",
        "platform_changed": False,
        "cancelled": False,
        "cancel_reason": None,
        "service_type": "train"
    }])
