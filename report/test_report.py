"""Testing file for report.py."""

import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
import email

from report import generate_pdf, get_email_message


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("SENDER_EMAIL", "trainee@yahoo.com")


@patch("report.SimpleDocTemplate")
def test_generate_pdf_build_called_once(mock_doc_template):
    """Tests that the build method is called once in generate_pdf()."""

    fake_pdf_buffer = BytesIO(b"fake_pdf_data")
    mock_report = MagicMock()

    mock_doc_template.return_value = mock_report

    with patch("report.BytesIO", return_value=fake_pdf_buffer):
        result = generate_pdf("London Paddington", {"Average Delay": 5})

    mock_report.build.assert_called_once()
    assert result == b"fake_pdf_data"


def test_get_email_message_correct_headers(mock_env):
    """Tests that correct headers present in email message."""

    station_name = "Huntingdon"
    fake_pdf = b"%PDF fake content"

    msg = get_email_message(station_name, fake_pdf)

    assert msg["Subject"] == f"{station_name} Summary Report"
    assert msg["From"] == "trainee@yahoo.com"


def test_get_email_message_correct_attachment_name(mock_env):
    """Tests that correct attachment name header present in email message."""

    station_name = "Huntingdon"
    fake_pdf = b"%PDF fake content"

    msg = get_email_message(station_name, fake_pdf)

    assert msg["Subject"] == f"{station_name} Summary Report"
    assert msg["From"] == "trainee@yahoo.com"
