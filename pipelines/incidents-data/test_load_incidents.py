"""Tests for load_incidents.py"""

from unittest.mock import patch

import pytest

from load_incidents import (get_operator_id_map,
                            get_station_id_map,
                            get_route_id,
                            insert_incidents)


def test_get_operator_id_map(fake_conn):
    """Test that the map is a dict of operator name: id."""
    cursor = fake_conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("Great Western Railway", 1), ("Elizabeth Line", 2)]

    result = get_operator_id_map(fake_conn)

    assert result == {"Great Western Railway": 1, "Elizabeth Line": 2}


def test_get_station_id_map(fake_conn):
    """Test that the map is a dict of station name: id."""
    cursor = fake_conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("London Paddington", 1), ("Bristol Temple Meads", 2)]

    result = get_station_id_map(fake_conn)

    assert result == {"London Paddington": 1, "Bristol Temple Meads": 2}


def test_get_route_id_success(fake_conn):
    """Get route id works correctly for stations and operator in database."""
    station_map = {"London Paddington": 1, "Bristol Temple Meads": 2}
    operator_map = {"Great Western Railway": 1}

    cursor = fake_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = [15]

    route_id = get_route_id(fake_conn, "London Paddington",
                            "Bristol Temple Meads", "Great Western Railway",
                            station_map, operator_map)

    assert route_id == 15


def test_get_route_id_missing_station_id(fake_conn):
    """Get route ID raises error if station is not in database."""
    station_map = {"London Paddington": 1}
    operator_map = {"Great Western Railway": 1}
    with pytest.raises(ValueError):
        get_route_id(fake_conn, "London Paddington",
                     "Bristol Temple Meads", "Great Western Railway", station_map, operator_map)


def test_get_route_id_missing_operator_id(fake_conn):
    """Get route ID raises error if operator is not in database."""
    station_map = {"London Paddington": 1, "Bristol Temple Meads": 2}
    operator_map = {"Elizabeth Line": 1}
    with pytest.raises(ValueError):
        get_route_id(fake_conn, "London Paddington",
                     "Bristol Temple Meads", "Great Western Railway", station_map, operator_map)


def test_route_caching(sample_extracted_data_pad_bri, fake_conn):
    """Test that get_route_id is only called if the route isn't cached."""
    with patch("load_incidents.get_route_id", return_value=1) as mock_get_route_id, \
            patch("load_incidents.get_existing_incident_keys", return_value={}), \
            patch("load_incidents.get_operator_id_map",
                  return_value={"Great Western Railway": 1}), \
            patch("load_incidents.get_station_id_map", return_value={
                "London Paddington": 1,
                "Bristol Temple Meads": 2}), \
            patch("load_incidents.publish_new_incident_to_topic", return_value=None):

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value
        fake_cursor.fetchone.return_value = [None]

        insert_incidents(fake_conn, sample_extracted_data_pad_bri)

        mock_get_route_id.assert_called_once_with(
            fake_conn,
            "London Paddington",
            "Bristol Temple Meads",
            "Great Western Railway",
            {"London Paddington": 1, "Bristol Temple Meads": 2},
            {"Great Western Railway": 1}
        )


def test_insert_incident_commits_once(fake_conn, sample_extracted_data_pad_bri):
    """Test that commit is called in insert incidents."""
    with patch("load_incidents.get_existing_incident_keys", return_value={}), \
            patch("load_incidents.get_operator_id_map",
                  return_value={"Great Western Railway": 1}), \
            patch("load_incidents.get_station_id_map", return_value={
                "London Paddington": 1,
                "Bristol Temple Meads": 2}), \
            patch("load_incidents.publish_new_incident_to_topic", return_value=None):

        fake_cursor = fake_conn.cursor.return_value.__enter__.return_value
        fake_cursor.fetchone.return_value = [None]

        insert_incidents(fake_conn, sample_extracted_data_pad_bri)

        fake_conn.commit.assert_called_once()
