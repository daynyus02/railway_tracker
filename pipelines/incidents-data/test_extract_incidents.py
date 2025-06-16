"""Tests for extract_incidents.py"""

from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from extract_incidents import (extract_relevant_data,
                               parse_xml,
                               get_incident_data)


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
        "summary": "CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June",
        "routes_affected": "<p>from Exeter St Davids to Exmouth</p>"
    }


# Test parse_xml


def test_parse_xml_valid_xml_input(sample_incident_xml_right_line):
    """Test that for an incident xml, it is in results."""
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
