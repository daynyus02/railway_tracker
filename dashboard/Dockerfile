FROM python:3.13

WORKDIR /app

COPY requirements.txt
RUN pip install --no-cash-dir -r requirements.txt

COPY pages/ .
COPY utils/ .
COPY .streamlit/ .
COPY logo.png .
COPY 📈_Live_Data.py
CMD ["streamlit", "run", "📈_Live_Data.py"]
