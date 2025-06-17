"""Script for creating PDF summary report."""

from os import environ as ENV

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
from boto3 import client
from botocore.exceptions import ClientError

from extract_report_data import get_days_data_per_station, get_db_connection
from transform_summary import get_station_summary


def generate_pdf(station_name: str, data: dict) -> bytes:
    """Generates summary report PDF for given station."""

    pdf_buffer = BytesIO()
    report = SimpleDocTemplate("myfile.pdf")
    styles = getSampleStyleSheet()

    styles['Title'].textColor = colors.HexColor("#df543b")
    styles['BodyText'].textColor = colors.HexColor("#3d3d3d")

    pdf_elements = []
    pdf_elements.append(
        Paragraph(f"OnTrack Summary Report, {dt.today().strftime("%d/%m/%Y")}, {station_name}", styles['Title']))
    for key, value in data.items():
        pdf_elements.append(Paragraph(f"{key}: {value}", styles['BodyText']))

    report.build(pdf_elements)

    pdf_buffer.seek(0)
    return pdf_buffer.read()


def get_email_message_as_string(station_name: str, pdf_bytes: bytes) -> str:
    """Gets the raw message string for summary email using PDF bytes."""

    msg = MIMEMultipart()
    msg['Subject'] = f"{station_name} Summary Report"
    msg['From'] = "trainee.stefan.cole@sigmalabs.co.uk"
    msg['To'] = "trainee.stefan.cole@sigmalabs.co.uk"

    body_text = "Here is your daily train summary report, see the PDF attached."
    msg.attach(MIMEText(body_text, 'plain'))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=f"{station_name} summary report {dt.today().strftime("%d/%m/%Y")}")
    msg.attach(attachment)

    return msg


def get_s3_client() -> client:
    """Returns an S3 client using boto3."""

    s3_client = client(
        "s3", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    return s3_client


def report_already_exists(bucket_name: str, filename: str) -> bool:
    """Returns true if a file with the given filename already exists in S3 bucket."""
    ...


if __name__ == "__main__":
    load_dotenv()

    with get_db_connection() as db_conn:
        station_data = DataFrame(get_days_data_per_station("DID", db_conn))
        summary = get_station_summary(station_data)
        generate_pdf("Didcot Parkway", summary)
