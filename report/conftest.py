"""Fixtures for testing report files."""

from pytest import fixture
from pandas import DataFrame


@fixture
def test_valid_past_day_data():
    """List of dictionaries with valid data for get_days_data_per_station function."""
    return [
        {
            "train_stop_id": 1,
            "train_service_id": 1,
            "scheduled_arr_time": "09:00:00",
            "actual_arr_time": "09:00:00",
            "scheduled_dep_time": "09:02:00",
            "actual_dep_time": "09:03:00",
            "platform": 2,
            "platform_changed": False,
            "station_id": 1,
            "station_name": "London Paddington",
            "station_crs": "PAD",
            "service_uid": "UID123",
            "train_identity": "U123",
            "service_date": "2025-06-10",
            "route_id": 1
        },
        {
            "train_stop_id": 4,
            "train_service_id": 2,
            "scheduled_arr_time": "10:00:00",
            "actual_arr_time": "10:00:00",
            "scheduled_dep_time": "10:02:00",
            "actual_dep_time": "10:02:00",
            "platform": 2,
            "platform_changed": False,
            "station_id": 1,
            "station_name": "London Paddington",
            "station_crs": "PAD",
            "service_uid": "UID124",
            "train_identity": "W123",
            "service_date": "2025-06-10",
            "route_id": 1
        },
        {
            "train_stop_id": 7,
            "train_service_id": 3,
            "scheduled_arr_time": "11:00:00",
            "actual_arr_time": "11:02:00",
            "scheduled_dep_time": "11:02:00",
            "actual_dep_time": "11:04:00",
            "platform": 2,
            "platform_changed": False,
            "station_id": 1,
            "station_name": "London Paddington",
            "station_crs": "PAD",
            "service_uid": "UID125",
            "train_identity": "J123",
            "service_date": "2025-06-10",
            "route_id": 1
        },
        {
            "train_stop_id": 10,
            "train_service_id": 4,
            "scheduled_arr_time": "12:00:00",
            "actual_arr_time": "12:05:00",
            "scheduled_dep_time": "12:02:00",
            "actual_dep_time": "12:07:00",
            "platform": 2,
            "platform_changed": False,
            "station_id": 1,
            "station_name": "London Paddington",
            "station_crs": "PAD",
            "service_uid": "UID126",
            "train_identity": "K123",
            "service_date": "2025-06-10",
            "route_id": 1
        }
    ]
