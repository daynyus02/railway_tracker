"""Testing file for extract script to create summary reports."""

from unittest.mock import MagicMock, patch
from psycopg2.extras import RealDictRow

from report.extract_reports import (get_db_connection, get_days_data_per_station,
                                    get_station_id_from_crs)


def test_get_db_connection_called_once():
    """Tests that connect gets called correctly in get_db_connection function."""
    with patch("extract_report_data.connect") as mock_connect, \
            patch.dict("os.environ", {
                "DB_USER": "USER",
                "DB_PASSWORD": "PASSWORD",
                "DB_HOST": "HOST",
                "DB_PORT": "PORT",
                "DB_NAME": "NAME"
            }):
        get_db_connection()
    mock_connect.assert_called_once()


def test_get_station_id_from_crs_true_with_valid_crs():
    """Tests that get_station_id function returns ID when valid CRS is passed."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = RealDictRow(
        {"station_id": 1, "station_name": "London Paddington", "station_crs": "PAD"})

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    assert get_station_id_from_crs("PAD", mock_conn) == 1


def test_get_station_id_from_crs_returns_none_crs_not_present():
    """Tests that get_station_id function returns None when CRS 
    does not correspond to a station in database."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    assert not get_station_id_from_crs("PAD", mock_conn)


@patch("extract_report_data.get_station_id_from_crs")
def test_days_data_per_station_returns_correct_data(fake_station_id, test_valid_past_day_data):
    """Tests that get_station_id function returns None when CRS 
    does not correspond to a station in database."""

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = test_valid_past_day_data

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    assert get_days_data_per_station(
        "PAD", mock_conn) == test_valid_past_day_data


@patch("extract_report_data.get_station_id_from_crs")
def test_days_data_per_station_returns_false_value_no_results(fake_station_id):
    """Tests that get_station_id function returns None when CRS 
    does not correspond to a station in database."""

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    assert not get_days_data_per_station(
        "PAD", mock_conn)
