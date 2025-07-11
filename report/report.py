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

from extract_reports import get_days_data_per_station, get_db_connection, get_station_name_from_crs
from transform_summary import get_station_summary


def generate_pdf(station_name: str, data: dict) -> bytes:
    """Generates summary report PDF for given station."""

    pdf_buffer = BytesIO()
    report = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()

    styles['Title'].textColor = colors.HexColor("#df543b")
    styles['BodyText'].textColor = colors.HexColor("#3d3d3d")

    pdf_elements = []
    pdf_elements.append(
        Paragraph(f"OnTrack {station_name} Summary Report, {dt.today().strftime("%d-%m-%Y")}", styles['Title']))
    for key, value in data.items():
        pdf_elements.append(Paragraph(f"{key}: {value}", styles['BodyText']))

    report.build(pdf_elements)

    pdf_buffer.seek(0)
    return pdf_buffer.read()


def get_email_message(station_name: str, pdf_bytes: bytes) -> MIMEMultipart:
    """Gets the raw message for summary email using PDF bytes."""

    msg = MIMEMultipart()
    msg['Subject'] = f"{station_name} Summary Report"
    msg['From'] = ENV["SENDER_EMAIL"]

    body_text = "Here is your daily train summary report, see the PDF attached."
    msg.attach(MIMEText(body_text, 'plain'))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=f"{station_name.lower().replace(" ", "_")}_station_summary_report_{dt.today().strftime("%d-%m-%Y")}.pdf")
    msg.attach(attachment)

    return msg
