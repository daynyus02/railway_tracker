"""Script for creating PDF summary report."""

from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO

from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pandas import DataFrame
from dotenv import load_dotenv

from extract import get_days_data_per_station, get_db_connection
from transform_summary import get_station_summary


def generate_pdf(station_crs: str, data: dict) -> bytes:
    """Generates summary report PDF for given station."""

    pdf_buffer = BytesIO()
    report = SimpleDocTemplate(
        f"{station_crs} summary report {dt.today().strftime("%d-%m-%Y")}.pdf")
    styles = getSampleStyleSheet()

    styles['Title'].textColor = colors.HexColor("#df543b")
    styles['BodyText'].textColor = colors.HexColor("#3d3d3d")

    pdf_elements = []
    pdf_elements.append(
        Paragraph(f"OnTrack {station_crs} Summary Report, {dt.today().strftime("%d-%m-%Y")}", styles['Title']))
    for key, value in data.items():
        pdf_elements.append(Paragraph(f"{key}: {value}", styles['BodyText']))

    report.build(pdf_elements)

    pdf_buffer.seek(0)
    return pdf_buffer.read()


def get_email_message_as_string(station_crs: str, pdf_bytes: bytes) -> str:
    """Gets the raw message string for summary email using PDF bytes."""

    msg = MIMEMultipart()
    msg['Subject'] = f"{station_crs} Summary Report"
    msg['From'] = "trainee.stefan.cole@sigmalabs.co.uk"
    msg['To'] = "trainee.stefan.cole@sigmalabs.co.uk"

    body_text = "Here is your daily train summary report, see the PDF attached."
    msg.attach(MIMEText(body_text, 'plain'))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=f"{station_crs} summary report {dt.today().strftime("%d-%m-%Y")}.pdf")
    msg.attach(attachment)

    return msg


if __name__ == "__main__":
    load_dotenv()

    with get_db_connection() as db_conn:
        station_data = DataFrame(get_days_data_per_station("DID", db_conn))
        summary = get_station_summary(station_data)
        generate_pdf("DID", summary)
