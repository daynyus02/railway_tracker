FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY utils/ utils/
COPY .streamlit .stremlit/
COPY logo.png .
COPY logo_words.png .
COPY live_data.py .
COPY historical_data.py .
COPY subscriptions.py .
COPY reports.py .
COPY dashboard.py .
CMD ["streamlit", "run", "dashboard.py"]
