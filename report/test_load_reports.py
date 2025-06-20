"""Testing file for loading reports to S3."""

import pytest
from unittest.mock import MagicMock, patch
import logging
from datetime import datetime as dt

from botocore.exceptions import ClientError

from load_reports import report_already_exists, load_new_report


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")


def test_report_already_exists_true(mock_env, caplog):
    """Tests that True is returned with correct log when file exists in bucket."""

    caplog.set_level(logging.INFO)

    mock_client = MagicMock()
    mock_client.head_object.return_value = {}

    res = report_already_exists(mock_client, "file.pdf")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == (
        "Report with filename file.pdf exists."
    )
    assert res


def test_report_already_exists_file_not_present(mock_env, caplog):
    """Tests that False is returned when file not present in bucket."""

    caplog.set_level(logging.INFO)

    mock_client = MagicMock()
    mock_client.head_object.side_effect = ClientError({
        'Error': {
            'Code': 'NoSuchKey'
        }
    }, "HeadObject")

    res = report_already_exists(mock_client, "other_report.pdf")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == (
        "other_report.pdf does not already exist in S3"
    )
    assert not res


def test_report_already_exists_file_raises_client_error(mock_env, caplog):
    """Tests that ClientError is returned when ClientError code not 404."""

    caplog.set_level(logging.INFO)

    mock_client = MagicMock()
    mock_client.head_object.side_effect = ClientError({
        'Error': {
            'Code': '500'
        }
    }, 'HeadObject')

    with pytest.raises(ClientError):
        res = report_already_exists(mock_client, "other_report.pdf")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == (
        "Error accessing S3 bucket to check for existing file."
    )


@patch("load.report_already_exists", return_value=False)
def test_load_new_report_correct_logs(mock_client, mock_env, caplog):

    caplog.set_level(logging.INFO)

    date_string = dt.today().strftime("%d-%m-%Y")

    mock_client.put_object.return_value = {}

    load_new_report(mock_client, "London Paddington", {})

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == (
        f"london_paddington_summary_report_{date_string}.pdf file successfully created in S3."
    )


@patch("load.report_already_exists", return_value=False)
def test_load_new_report_correct_error_logs(mock_client, mock_env, caplog):

    caplog.set_level(logging.INFO)

    mock_client.put_object.side_effect = ClientError({
        'Error': {
            'Code': '500',
            'Message': 'Unknown'
        }
    }, 'PutObject')

    load_new_report(mock_client, "London Paddington", {})

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == (
        "Failed to load report to S3 bucket: An error occurred (500) when calling the PutObject operation: Unknown."
    )
