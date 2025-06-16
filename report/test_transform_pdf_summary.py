"""Tests for transform script to create PDF summary report."""

from datetime import timedelta as td

from transform_pdf_summary import (get_pct_trains_dep_delayed_five_mins,
                                   get_pct_trains_arr_delayed_five_mins,
                                   get_avg_dep_delay_all_trains, get_pct_trains_cancelled,
                                   get_avg_arr_delay_all_trains,
                                   get_avg_dep_delay_delayed_trains,
                                   get_avg_arr_delay_delayed_trains,
                                   convert_timedelta_to_str)


# convert_timedelta_to_str() tests

def test_convert_timedelta_to_str_zero():
    """Tests that correct string returned from zero timedelta."""

    assert convert_timedelta_to_str(
        td(days=0, hours=0, minutes=0, seconds=0)) == "00:00:00"


def test_convert_timedelta_to_str_non_zero():
    """Tests that correct string returned from non-zero timedelta."""

    assert convert_timedelta_to_str(
        td(days=0, hours=1, minutes=3, seconds=1)) == "01:03:01"


def test_convert_timedelta_to_str_one_days():
    """Tests that correct string returned from timedelta with 1 day."""

    assert convert_timedelta_to_str(
        td(days=1, hours=1, minutes=3, seconds=1)) == "1 day 1:03:01"


def test_convert_timedelta_to_str_multiple_days():
    """Tests that correct string returned from timedelta with 2 days."""

    assert convert_timedelta_to_str(
        td(days=2, hours=1, minutes=3, seconds=1)) == "2 days 1:03:01"

# get_pct_trains_dep_delayed_five_mins() tests


def test_get_pct_trains_dep_delayed_five_mins_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have departure delays at least five minutes."""

    assert get_pct_trains_dep_delayed_five_mins(past_day_data_no_delays) == 0


def test_get_pct_trains_dep_delayed_five_mins_returns_correct_pct_one_delay(past_day_data_long_delays):
    """Tests that correct percentage is returned when one train has departure delays at least five minutes."""

    assert get_pct_trains_dep_delayed_five_mins(
        past_day_data_long_delays) == 50


# get_pct_trains_arr_delayed_five_mins() tests

def test_get_pct_trains_arr_delayed_five_mins_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have arrival delays at least five minutes."""

    assert get_pct_trains_arr_delayed_five_mins(past_day_data_no_delays) == 0


def test_get_pct_trains_arr_delayed_five_mins_returns_correct_pct_one_delay(past_day_data_long_delays):
    """Tests that correct percentage is returned when one train has arrival delays at least five minutes."""

    assert get_pct_trains_arr_delayed_five_mins(
        past_day_data_long_delays) == 50


# get_pct_trains_cancelled() tests

def test_get_pct_trains_cancelled_no_cancellations(past_day_data_no_delays):
    """Tests that zero is returned when no trains are cancelled."""

    assert get_pct_trains_cancelled(past_day_data_no_delays) == 0


def test_get_pct_trains_cancelled_returns_correct_pct_one_cancellation(past_day_data_cancellation):
    """Tests that correct percentage is returned when one train is cancelled."""

    assert get_pct_trains_cancelled(past_day_data_cancellation) == 50


# get_avg_dep_delay_all_trains() tests

def test_get_avg_dep_delay_all_trains_returns_zero(past_day_data_no_delays):
    """Tests that zero string is returned when no trains have departure delays."""

    assert get_avg_dep_delay_all_trains(past_day_data_no_delays) == "00:00:00"


def test_get_avg_dep_delay_all_trains_returns_correct_str_one_delay(past_day_data_long_delays):
    """Tests that correct time str is returned when one train has departure delays."""

    assert get_avg_dep_delay_all_trains(
        past_day_data_long_delays) == "00:02:30"


def test_get_avg_dep_delay_all_trains_returns_correct_str_early_departure(past_day_data_early):
    """Tests that correct time str is returned when one train has early departure."""

    assert get_avg_dep_delay_all_trains(
        past_day_data_early) == "00:01:30"


# get_avg_dep_delay_delayed_trains() tests

def test_get_avg_dep_delay_delayed_trains_returns_correct_str_early_arrival(past_day_data_early):
    """Tests that correct time str for delays among delayed trains is returned when one train has early departure."""

    assert get_avg_dep_delay_delayed_trains(
        past_day_data_early) == "00:03:00"


# get_avg_arr_delay_all_trains() tests

def test_get_avg_arr_delay_all_trains_returns_zero(past_day_data_no_delays):
    """Tests that zero string is returned when no trains have arrival delays."""

    assert get_avg_arr_delay_all_trains(past_day_data_no_delays) == "00:00:00"


def test_get_avg_arr_delay_all_trains_returns_correct_str_one_delay(past_day_data_long_delays):
    """Tests that correct time str is returned when one train has arrival delays."""

    assert get_avg_arr_delay_all_trains(
        past_day_data_long_delays) == "00:04:30"


def test_get_avg_arr_delay_all_trains_returns_correct_str_early_arrival(past_day_data_early):
    """Tests that correct time str is returned when one train has early arrival."""

    assert get_avg_arr_delay_all_trains(
        past_day_data_early) == "00:01:30"


# get_avg_arr_delay_delayed_trains() tests

def test_get_avg_arr_delay_delayed_trains_returns_correct_str_early_arrival(past_day_data_early):
    """Tests that correct time str for delays among delayed trains is returned when one train has early arrival."""

    assert get_avg_arr_delay_delayed_trains(
        past_day_data_early) == "00:03:00"
