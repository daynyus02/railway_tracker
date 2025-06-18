from os import environ as ENV

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

    except Exception:
        st.error("AWS credentials not found.")
        return []

def generate_presigned_url(bucket_name, key, client, expiration=3600):
    """Generate a pre-signed URL for the given S3 object."""
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        st.error(f"Error generating URL: {e}")
        return None

load_dotenv()
s3_client = boto3.client('s3', 
                            region_name=ENV["REGION"],
                            aws_access_key_id=ENV["ACCESS_KEY"],
                            aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])


BUCKET_NAME = 'c17-trains-reports'

st.title("📂 Download PDF Reports:")

pdf_keys = list_pdfs(BUCKET_NAME, s3_client)

if pdf_keys:
    for i in range(len(pdf_keys)):
        file_name = pdf_keys[i].split('/')[-1]
        url = generate_presigned_url(BUCKET_NAME, pdf_keys[i], s3_client)
        if url:
            st.markdown(f"**{i+1}.** [📄 {file_name}]({url})", unsafe_allow_html=True)
else:
    st.write("No PDF files found.")
