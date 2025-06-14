"""Script to clean the raw train data."""
import logging

from datetime import datetime, time

from dotenv import load_dotenv

import pandas as pd
from pandas import DataFrame

from extract import fetch_train_data

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "service_uid", "train_identity", "station_name", "station_crs",
    "origin_name", "destination_name", "scheduled_arr_time", "actual_arr_time",
    "scheduled_dep_time", "actual_dep_time", "operator_name",
    "service_date", "platform", "platform_changed", "cancelled", "cancel_reason",
    "service_type"
]

CRITICAL_COLUMNS = [
    "service_uid", "train_identity", "station_name", "station_crs",
    "origin_name", "destination_name", "operator_name", "service_date",
    "platform", "platform_changed", "cancelled"
]


def check_all_required_columns_present(data: DataFrame) -> None:
    """Checking if all columns required are present."""
    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        logger.error("Missing columns: %s", missing_columns)
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}")
    logger.info("All required columns are present.")


def filter_trains(data: DataFrame) -> DataFrame:
    """Returning a dataframe that only has data relevant to train services."""
    logger.info("Filtering rows by service type: train")
    filtered_train_data = data[data['service_type'].str.lower() == 'train']
    logger.debug("Initial rows: %s, Filtered rows: %s",
                 len(data), len(filtered_train_data))
    return filtered_train_data.drop(columns=["service_type"])


def drop_rows_with_missing_critical_data(data: DataFrame) -> DataFrame:
    """Returning a dataframe that doesn't have rows with missing critical data."""
    logger.info("Dropping rows that have missing critical data.")
    valid_data = data.dropna(subset=CRITICAL_COLUMNS).reset_index(drop=True)
    logger.debug("Number of dropped rows: %s", len(data) - len(valid_data))
    return valid_data


def convert_time_columns(data: DataFrame) -> DataFrame:
    """Returning a dataframe with correct time column formats."""
    time_columns = [
        'scheduled_arr_time', 'actual_arr_time',
        'scheduled_dep_time', 'actual_dep_time'
    ]

    def convert_hhmm_to_time(time_string) -> time:
        if pd.isna(time_string) or time_string == '':
            return None
        try:
            return datetime.strptime(time_string, '%H%M').time()
        except ValueError:
            return None

    for col in time_columns:
        logger.debug("Changing %s column to have correct time format.", col)
        if col in data.columns:
            data[col] = data[col].apply(convert_hhmm_to_time)
    logger.info("All time format changes applied.")
    return data


def convert_date_column(data: DataFrame) -> DataFrame:
    """Returning a dataframe with correct date formats."""
    logger.info("Changing all service_date rows to date data type.")
    data['service_date'] = pd.to_datetime(
        data['service_date'], errors='coerce').dt.date
    logger.info("Changes to service_date have been applied.")
    return data


def convert_platform_changed_to_bool(data: DataFrame) -> DataFrame:
    """Returning a dataframe that has boolean values inside the `platform_changed` column."""
    logger.debug("Changing all platform_changed rows to boolean data type.")
    data["platform_changed"] = data["platform_changed"].astype(str).str.lower().map(
        {"true": True, "1": True, "false": False, "0": False}
    ).astype(bool)
    logger.info("Changes to platform_changed have been applied.")
    return data


def convert_cancelled_to_bool(data: DataFrame) -> DataFrame:
    """Returning a dataframe that has boolean values inside the `cancelled` column."""
    logger.debug("Changing all cancelled rows to boolean data type.")
    data["cancelled"] = data["cancelled"].astype(str).str.lower().map(
        {"true": True, "1": True, "false": False, "0": False}
    ).astype(bool)
    logger.info("Changes to cancelled have been applied.")
    return data


def transform_train_data(data: DataFrame) -> DataFrame:
    """Returns fully transformed data for load stage of ETL."""
    try:
        logger.info("Starting transform.")
        check_all_required_columns_present(data)
        data = filter_trains(data)
        data = drop_rows_with_missing_critical_data(data)
        data = convert_time_columns(data)
        data = convert_date_column(data)
        data = convert_platform_changed_to_bool(data)
        data = convert_cancelled_to_bool(data)
        logger.info("Data has been transformed successfully.")
        logger.info("Final row count after transformation: %s", len(data))
        return data
    except Exception as e:
        logger.exception("Transform failed: %s", e)
        raise


if __name__ == "__main__":
    load_dotenv()
    stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
    result = fetch_train_data(stations)
    transformed_data = transform_train_data(result)
