# pylint: skip-file

# pylint: disable=invalid-name, non-ascii-file-name
"""A page to download daily reports."""
from os import environ as ENV
import botocore.exceptions

import boto3
import streamlit as st
from dotenv import load_dotenv


def list_pdfs(bucket_name, client):
    """List all PDF files in the given S3 bucket and prefix."""
    try:
        response = client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            return []

        pdf_files = [
            obj['Key'] for obj in response['Contents']
            if obj['Key'].endswith('.pdf')
        ]
        return pdf_files

    except botocore.exceptions.ClientError as e:
        st.error(f"AWS Client Error: {e.response['Error']['Message']}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []

def generate_url(bucket_name, object_key, client, expiration=3600):
    """Generate a pre-signed URL for the given S3 object."""
    try:
        report_url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
        return report_url
    except Exception as e:
        st.error(f"Error generating URL: {e}")
        return None

load_dotenv()
s3_client = boto3.client('s3',
                            region_name=ENV["REGION"],
                            aws_access_key_id=ENV["ACCESS_KEY"],
                            aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])

st.title("📂 Download PDF Reports:")

pdf_keys = list_pdfs(ENV["BUCKET_NAME"], s3_client)

if pdf_keys:
    for i, key in enumerate(pdf_keys, start=1):
        file_name = key.split('/')[-1]
        url = generate_url(ENV["BUCKET_NAME"], key, s3_client)
        if url:
            st.link_button(f"{i}. 📄 {file_name}", url)
else:
    st.write("No PDF files found.")

