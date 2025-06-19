"""Testing file for report.py."""


from io import BytesIO
from unittest.mock import patch, MagicMock

from report import generate_pdf


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
