"""Tests for alerts_incidents.py"""

from unittest.mock import MagicMock
from pandas import Timestamp

from alerts_incidents import (get_subject, get_message, get_sns_topic_arn)


def test_get_sns_topic_arn():
    """Test it will return a topic arn as expected."""
    mock_sns_client = MagicMock()
    mock_sns_client.create_topic.return_value = {
        "TopicArn": "fake topic arn"
    }

    result = get_sns_topic_arn(mock_sns_client, "ABC", "XYZ")

    assert result == "fake topic arn"
    mock_sns_client.create_topic.assert_called_once_with(
        Name="c17-trains-incidents-ABC-XYZ"
    )


def test_get_subject_new():
    """Test a subject for a new incident is created as expected."""
    start_time = Timestamp("2025-07-20T00:00:00Z")
    expected_subject = "New incident on route PAD to BRI from 2025-07-20."
    assert get_subject("PAD", "BRI", start_time, True) == expected_subject


def test_get_subject_update():
    """Test a subject for an updated incident is created as expected."""
    start_time = Timestamp("2025-07-20T00:00:00Z")
    expected_subject = "There has been an update to an incident on route PAD to BRI from " \
        "2025-07-20."
    assert get_subject("PAD", "BRI", start_time, False) == expected_subject


def test_get_message_planned():
    """Test a message for a planned incident is created as expected."""
    summary = "summary"
    info_link = "link"
    start_time = Timestamp(
        "2025-07-20T00:00:00Z").tz_convert("Europe/London").tz_localize(None)
    end_time = Timestamp("2025-07-20T22:59:00Z")

    expected_message = "summary.\n\nThe incident will take place from 2025-07-20 01:00:00" \
        " until 2025-07-20 23:59:00.\n\nFor more information, please visit link."
    assert get_message(summary, info_link, start_time,
                       end_time, True) == expected_message


def test_get_message_unplanned():
    """Test a message for an unplanned incident is created as expected."""
    summary = "summary"
    info_link = "link"
    start_time = Timestamp(
        "2025-07-20T00:00:00Z").tz_convert("Europe/London").tz_localize(None)
    end_time = Timestamp("2025-07-20T23:59:00Z")

    expected_message = "summary.\n\nThe incident will take place from 2025-07-20 01:00:00." \
        "\n\nFor more information, please visit link."
    assert get_message(summary, info_link, start_time,
                       end_time, False) == expected_message
