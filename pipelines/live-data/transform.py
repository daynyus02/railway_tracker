"""Script to clean the raw train data."""
import logging

from datetime import date, time

from dotenv import load_dotenv
from pandas import DataFrame

from extract import fetch_train_data

logging.basicConfig(
    level="WARNING",
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


def check_all_required_columns_present(data: DataFrame, required_columns=REQUIRED_COLUMNS):
    """Checking if all columns required are present."""
    missing_columns = [
        col for col in required_columns if col not in data.columns]
    if missing_columns:
        logger.error("Missing columns: %s", missing_columns)
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}")
    logger.info("All required columns are present.")


def filter_trains(data: DataFrame) -> DataFrame:
    """Returning a dataframe that only has data relevant to train services."""
    logger.info("Filtering rows by service type: train")
    filtered_train_data = data[data['service_type'].str.lower() == 'train']
    logger.info("Number of removed rows: %s",
                len(data) - len(filtered_train_data))
    return filtered_train_data.drop(columns=["service_type"])


def drop_rows_with_missing_critical_data(data: DataFrame) -> DataFrame:
    """Returning a dataframe that doesn't have rows with missing critical data."""
    logger.info("Dropping rows that have missing critical data.")
    valid_data = data.dropna(subset=CRITICAL_COLUMNS).reset_index(drop=True)
    logger.info("Number of dropped rows: %s", len(data) - len(valid_data))
    return valid_data


def transform_train_data(data: DataFrame) -> DataFrame:
    """Returns fully transformed data for load stage of ETL."""
    check_all_required_columns_present(data)
    data = filter_trains(data)
    data = drop_rows_with_missing_critical_data(data)
    print(data.info())
    return data


if __name__ == "__main__":
    load_dotenv()
    stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
    result = fetch_train_data(stations)
    transformed_data = transform_train_data(result)
    print(len(result), len(transformed_data))
    transformed_data.to_csv("trains.csv", index=False)
