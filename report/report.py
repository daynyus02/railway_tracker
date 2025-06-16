"""Script for creating PDF summary report."""

import json

from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO

import boto3
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from pandas import DataFrame

from extract_report_data import get_days_data_per_station


def generate_pdf(data: DataFrame) -> bytes:
    """Generates summary report PDF for given station."""

    pdf_buffer = BytesIO()
    report = SimpleDocTemplate("myfile.pdf")
    styles = getSampleStyleSheet()

    pdf_elements = []
    pdf_elements.append(Paragraph("Train Summary Report", styles["Heading1"]))
    pdf_elements.append(Paragraph("Something", styles["BodyText"]))
    pdf_elements.append(Paragraph("Something", styles["BodyText"]))
    pdf_elements.append(Paragraph("Something else", styles["BodyText"]))
    pdf_elements.append(Paragraph("Something further", styles["BodyText"]))

    report.build(pdf_elements)

    pdf_buffer.seek(0)
    return pdf_buffer.read()


def get_email_message_as_string(pdf_bytes: bytes) -> str:
    """Gets the raw message string for summary email using PDF bytes."""

    msg = MIMEMultipart()
    msg['Subject'] = "Train Summary Report"
    msg['From'] = "trainee.stefan.cole@sigmalabs.co.uk"
    msg['To'] = "trainee.stefan.cole@sigmalabs.co.uk"

    body_text = "Here is your daily train summary report, see the PDF attached."
    msg.attach(MIMEText(body_text, 'plain'))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header('Content-Disposition', 'attachment',
                          filename=f"Train summary report {dt.today}")
    msg.attach(attachment)


if __name__ == "__main__":
    generate_pdf()
