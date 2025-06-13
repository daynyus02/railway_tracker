# pylint: skip-file
"""Unit testing for the functions in transform.py."""

from datetime import date, time
import pandas as pd
import pytest
from pandas import DataFrame
import numpy as np

from transform import (
    check_all_required_columns_present,
    filter_trains,
    drop_rows_with_missing_critical_data,
    convert_time_columns,
    convert_date_column,
    convert_platform_changed_to_bool,
    convert_cancelled_to_bool,
    transform_train_data
)


def test_check_all_required_columns_present_raises_error(test_data):
    test_df = test_data.copy()
    test_df = test_data.drop(columns=["service_uid"])
    with pytest.raises(ValueError, match="Missing required columns"):
        check_all_required_columns_present(test_df)


def test_filter_trains_removes_non_trains(test_data):
    test_df = test_data.copy()
    test_df.loc[0, "service_type"] = "bus"
    result = filter_trains(test_df)
    assert result.empty


def test_drop_rows_with_missing_critical_data_removes_incomplete_rows(test_data):
    test_df = test_data.copy()
    test_df.loc[0, "service_uid"] = None
    result = drop_rows_with_missing_critical_data(test_df)
    assert result.empty


def test_convert_time_columns(test_data):
    test_df = convert_time_columns(test_data.copy())
    assert test_df["scheduled_arr_time"].iloc[0].hour == 12
    assert test_df["actual_arr_time"].iloc[0].minute == 45


def test_convert_date_column(test_data):
    test_df = convert_date_column(test_data.copy())
    assert test_df["service_date"].iloc[0].year == 2024
    assert test_df["service_date"].iloc[0].month == 5
    assert test_df["service_date"].iloc[0].day == 1


@pytest.mark.parametrize("input_value,expected", [
    (True, True),
    (False, False),
    (np.bool_(True), True),
    ("TRUE", True),
    ("FALSE", False),
    (1, True),
    (0, False),
])
def test_convert_cancelled_to_bool(input_value, expected):
    test_df = DataFrame({"cancelled": [input_value]})
    result = convert_cancelled_to_bool(test_df.copy())
    assert result["cancelled"].iloc[0] == expected


@pytest.mark.parametrize("input_value,expected", [
    (True, True),
    (False, False),
    (np.bool_(True), True),
    ("TRUE", True),
    ("FALSE", False),
    (1, True),
    (0, False),
])
def test_convert_platform_changed_to_bool(input_value, expected):
    test_df = DataFrame({"platform_changed": [input_value]})
    result = convert_platform_changed_to_bool(test_df.copy())
    assert result["platform_changed"].iloc[0] == expected


def test_transform_train_data_success(test_data):
    result = transform_train_data(test_data.copy())

    assert "service_type" not in result.columns
    assert isinstance(result["scheduled_arr_time"].iloc[0], time)
    assert isinstance(result["actual_dep_time"].iloc[0], time)
    assert isinstance(result["service_date"].iloc[0], date)
