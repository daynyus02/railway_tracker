# 🚆 Railway Tracker by [logo](./OnTrack.png) OnTrack

A cost-effective, end-to-end data pipeline and reporting platform for monitoring train service status across the UK rail network.

## Overview

We’ve all experienced the frustration—standing on a freezing platform, staring at a board that keeps updating, or worse, shows nothing at all.
There’s a widespread perception that the UK railway is among the worst in Europe, but how accurate is that belief?

The problem we identified is not just service reliability, but the lack of clear, accessible data that gives passengers a true picture of what’s happening across the rail network.

Our solution at OnTrack brings together three main services:

- **Delay and incident alerts** - Emails automatically sent to subscribers to inform them about delays on their chosen route, plus incidents causing disruption such as engineering works published officially by National Rail.

- **Daily summary reports** - PDF reports generated for each of our tracked stations, with data about the incidence and severity of delays and cancellations affecting services from the previous day.

- **Online dashboard** - Live dashborad displaying departure and arrival information, with an accessible format with interactive elements allowing users to select relevant stations and times to suit their travelling needs.

## Roles

| Member    | Role                            |
|-----------|---------------------------------|
| Daynyus   | Data Engineer, Project Manager  |
| Will      | Data Engineer, Quality Assurance|
| Tom       | Data Engineer, Architect        |
| Stefan    | Data Engineer, Architect        |

## Features

- Automated data ingestion every from APIs
- Live dashboard with a train timetable and summary statistics
- Daily summary reports per station
- Alerts for delayed and cancelled trains
- Alerts for new or updated incidents affecting train services

## Architecture

- Data Ingestion: Lambda function pulls incident data from the Realtime Trains API every minute, and National Rail Incidents API before storing it in PostgreSQL (RDS).
- Alerting: SNS topics send alerts for delays, cancellations and incidents on watched routes.
- Reporting: Daily scheduled Lambda queries the database and generates summary reports per station.

## Repository Structure

## Getting Started

## Tech Stack