"""Tests for transform script to create PDF summary report."""

from transform_pdf_summary import (get_pct_trains_dep_delayed_five_mins,
                                   get_pct_trains_arr_delayed_five_mins,
                                   get_avg_dep_delay_all_trains, get_pct_trains_cancelled,
                                   get_avg_arr_delay_all_trains,
                                   get_avg_dep_delay_delayed_trains,
                                   get_avg_arr_delay_delayed_trains)


def test_get_pct_trains_dep_delayed_five_mins_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have departure delays over five minutes."""

    assert get_pct_trains_dep_delayed_five_mins(past_day_data_no_delays) == 0


def test_get_pct_trains_dep_delayed_five_mins_returns_correct_pct_one_delay(past_day_data_long_delays):
    """Tests that correct percentage is returned when one train has departure delays over five minutes."""

    assert get_pct_trains_dep_delayed_five_mins(
        past_day_data_long_delays) == 50


def test_get_pct_trains_arr_delayed_five_mins_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have arrival delays over five minutes."""

    assert get_pct_trains_arr_delayed_five_mins(past_day_data_no_delays) == 0


def test_get_pct_trains_arr_delayed_five_mins_returns_correct_pct_one_delay(past_day_data_long_delays):
    """Tests that correct percentage is returned when one train has arrival delays over five minutes."""

    assert get_pct_trains_arr_delayed_five_mins(
        past_day_data_long_delays) == 50


def test_get_pct_trains_cancelled_no_cancellations(past_day_data_no_delays):
    """Tests that zero is returned when no trains are cancelled."""

    assert get_pct_trains_cancelled(past_day_data_no_delays) == 0


def test_get_pct_trains_cancelled_returns_correct_pct_one_cancellation(past_day_data_cancellation):
    """Tests that correct percentage is returned when one train is cancelled."""

    assert get_pct_trains_cancelled(past_day_data_cancellation) == 50


def test_get_avg_dep_delay_all_trains_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have departure delays."""

    assert get_avg_dep_delay_all_trains(past_day_data_no_delays) == 0


def test_get_avg_dep_delay_all_trains_returns_correct_int_one_delay(past_day_data_long_delays):
    """Tests that correct integer is returned when one train has departure delays."""

    assert get_avg_dep_delay_all_trains(
        past_day_data_long_delays) == 2.5


def test_get_avg_dep_delay_all_trains_returns_correct_float_early_arrival(past_day_data_early):
    """Tests that correct float is returned when one train has early arrival."""

    assert get_avg_arr_delay_all_trains(
        past_day_data_early) == 1.5


def test_get_avg_dep_delay_delayed_trains_returns_correct_float_early_arrival(past_day_data_early):
    """Tests that correct float for delays among delayed trains is returned when one train has early departure."""

    assert get_avg_dep_delay_delayed_trains(
        past_day_data_early) == 3


def test_get_avg_arr_delay_all_trains_returns_zero(past_day_data_no_delays):
    """Tests that zero is returned when no trains have arrival delays."""

    assert get_avg_arr_delay_all_trains(past_day_data_no_delays) == 0


def test_get_avg_arr_delay_all_trains_returns_correct_float_one_delay(past_day_data_long_delays):
    """Tests that correct float is returned when one train has arrival delays."""

    assert get_avg_arr_delay_all_trains(
        past_day_data_long_delays) == 4.5


def test_get_avg_arr_delay_all_trains_returns_correct_float_early_arrival(past_day_data_early):
    """Tests that correct float is returned when one train has early arrival."""

    assert get_avg_arr_delay_all_trains(
        past_day_data_early) == 1


def test_get_avg_arr_delay_delayed_trains_returns_correct_float_early_arrival(past_day_data_early):
    """Tests that correct float for delays among delayed trains is returned when one train has early arrival."""

    assert get_avg_arr_delay_delayed_trains(
        past_day_data_early) == 2
