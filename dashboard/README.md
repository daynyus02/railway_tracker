## Dashboard

### Overview
This directory contains the scripts which set up and run the 'Railway Tracker' dashboard.

Explanation
This directory is needed to provide the data to the live dashboard, allowing users to get live and historical train information.

Setup and Installation
[Any necessary steps for setting up the directory + installing dependencies]
1. Set up a venv by running `python -m venv .venv`.
2. Activate the venv by running `.venv/bin/activate`.
3. Run `pip3 install -r requirements.txt` to install necessary requirements.

Usage
[Instructions for using files in the directory]
1. To run the dashboard locally, run `streamlit run dashboard.py`.
2. Additionally, to build a docker image that runs this dashboard, run `docker build -t <name of image>`



