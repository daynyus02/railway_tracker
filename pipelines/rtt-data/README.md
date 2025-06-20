## 📊 Live-Data 📊
This directory contains the ETL pipeline for the Realtime Trains API. 

This pipeline **extracts** train service data from the Realtime Trains API and processes it into a structured DataFrame format containing scheduled and actual arrival/departure times, platform changes, cancellations, and more. The data is then **transformed** before being **uploaded** to an RDS database hosted on AWS RDS. During the load phase the script also sends out notifications of new/updated delayed trains.

### 📁 Files 📁
- **extract.py**  
    Contains functions to fetch live train service data based on a station's CRS and extract only data required for analysis.

- **test_extract.py**  
    Contains unit tests for the functions in extract.py.

- **transform.py**  
    Contains functions used to transform data fetched by the extract.py script. It prepares the raw data for the load phase by cleaning, validating, and converting it into the correct data types (e.g. time, date, boolean).

- **test_extract.py**  
    Contains unit tests for the functions in transform.py.

- **load.py**  
    Contains functions used to load and update the database with transformed data from the transform.py script. 

- **test_load.py**  
    Contains unit tests for the functions in load.py.

- **alerts.py**  
    Contains functions used to filter out delayed trains for specific routes and send them to their corresponding topics.

- **test_alerts.py**  
    Contains unit tests for the functions in alerts.py
    
- **conftest.py**  
    Contains fixtures for the tests.

- **main.py**  
    Serves as the main entry point of the ETL pipeline. It orchestrates extraction, transformation, and loading of train service data. Includes a lambda_handler function to enable execution in an AWS Lambda environment for automation.




### 🛠️ Setup and Installation 🛠️
**Any necessary steps for setting up the directory + installing dependencies**

1. Create and activate a new virtual environment 
- `python3 -m venv .venv`
- `source .venv/bin/activate`
2. Install all dependencies.
- `pip install -r requirements.txt`
3. Ensure that environment variables are stored locally in a .env file, such as AWS and Realtime Trains credentials

### Example `.env`
```
API_USERNAME=X
API_PASSWORD=X

DB_HOST=X
DB_NAME=X
DB_USER=X
DB_PASSWORD=X
DB_PORT=X

STATIONS=X,X,X,X,X...
```

### ⏳ Usage ⌛️
**Instructions for using files in the directory**  
1.  Build a docker file with `docker build -t [tag_name] .`
2.  Run the image with `docker run --env-file .env [tag_name]`




