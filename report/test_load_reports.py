"""Testing file for loading reports to S3."""

from os import environ as ENV
from pytest import fixture
from unittest.mock import MagicMock
import logging

from botocore.exceptions import ClientError

from load import report_already_exists


@fixture
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
    ...
