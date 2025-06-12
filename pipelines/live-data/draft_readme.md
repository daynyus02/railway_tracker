## 📊 Live-Data 📊
This directory contains the ETL pipeline for the Realtime Trains API. 

This pipeline **extracts** train service data from the Realtime Trains API and processes it into a structured DataFrame format containing scheduled and actual arrival/departure times, platform changes, cancellations, and more. The data is then **transformed** before being **uploaded** to an RDS database hosted on AWS RDS.

### 📁 Files 📁
- **extract.py**  
    Contains the functions to fetch live train service data based on a station's CRS and extract only data required for analysis.

### 🛠️ Setup and Installation 🛠️
**Any necessary steps for setting up the directory + installing dependencies**

1. Create and activate a new virtual environment 
- `python3 -m venv .venv`
- `source .venv/bin/activate`
2. Install all dependencies.
- `pip install -r requirements.txt`
3. Ensure that environment variables are stored locally in a .env file, such as AWS and Realtime Trains credentials

### ⏳ Usage ⌛️
**Instructions for using files in the directory**  
1.  
2.  
3.  
