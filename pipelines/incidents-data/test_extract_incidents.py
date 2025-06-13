"""Tests for extract.py"""

from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

import pytest

from extract_incidents import (is_paddington_to_bristol,
                               extract_relevant_data, parse_xml, get_incident_data)

# Test is_paddington_to_bristol


@pytest.mark.parametrize("text,expected", [
    ("between London Paddington and Bristol Temple Meads", True),
    ("Between London Paddington and Reading / Bristol Temple Meads / Cheltenham", True),
    ("between Reading and Bristol Temple Meads", False),
    ("Paddington to Bristol", False),
    ("from london paddington to bristol temple meads", True)
])
def test_is_paddington_to_bristol_valid_input(text, expected):
    """Test that it correctly validates a paddington -> bristol line."""
    assert is_paddington_to_bristol(text) == expected


# Test extract_relevant_data


def test_extract_relevant_data(sample_incident_xml_wrong_line):
    """Tests that data is extracted as expected."""
    ns = {
        'inc': 'http://nationalrail.co.uk/xml/incident',
        'com': 'http://nationalrail.co.uk/xml/common'
    }

    element = ET.fromstring(sample_incident_xml_wrong_line)
    incident = element.find("inc:PtIncident", namespaces=ns)
    result = extract_relevant_data(ns, incident)

    assert result == {
        "start_time": "2025-06-09T00:00:00.000+01:00",
        "end_time": "2025-06-13T23:59:00.000+01:00",
        "description": "<p>The evening engineering work scheduled to take place between Exeter St Davids and Exmouth on Monday to Thursday nights has been cancelled</p>",
        "incident_number": "DA3DF5FDF4074F90BE871AAB6F0B8D1F",
        "version_number": "20250602082813",
        "is_planned": "true",
        "info_link": "https://www.nationalrail.co.uk/engineering-works/23-40-exd-exm-20250609/",
        "summary": "CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June"
    }


# Test parse_xml


def test_parse_xml_wrong_line(sample_incident_xml_wrong_line):
    """Test that for an incident not on paddington -> bristol line, it is skipped over."""
    mock_response = Mock()
    mock_response.text = sample_incident_xml_wrong_line
    result = parse_xml(mock_response)

    assert not result


def test_parse_xml_right_line(sample_incident_xml_right_line):
    """Test that for an incident on paddington -> bristol line, it is in results."""
    mock_response = Mock()
    mock_response.text = sample_incident_xml_right_line
    result = parse_xml(mock_response)

    assert result


# Testing get_incident_data


def test_get_incident_data():
    """Patch requests and test that it calls correctly."""
    with patch("requests.get") as mock_get, \
            patch.dict("os.environ", {"GW_URL": "URL"}):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<PiIncident></PiIncident>"
        mock_get.return_value = mock_response

        response = get_incident_data()
        assert response.status_code == 200
        assert "<PiIncident>" in response.text
