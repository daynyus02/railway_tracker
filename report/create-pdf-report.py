"""Script for creating PDF summary report."""

import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from io import BytesIO
from reportlab.platypus import Paragraph, SimpleDocTemplate

from pandas import DataFrame


def generate_pdf(data: DataFrame) -> bytes:
    """Generates summary report PDF for given station."""

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer)

    pdf_elements = []
    pct_trains_dep_delayed = Paragraph(f"Something")
    pct_trains_cancelled = Paragraph(f"Something")
    avg_dep_delay = Paragraph(f"Something else")
    avg_arr_delay = Paragraph("Something further")

    doc.save()
    pdf_buffer.seek(0)
    return pdf_buffer.read()
