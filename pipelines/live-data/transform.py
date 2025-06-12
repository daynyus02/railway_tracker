"""Script to clean the raw train data."""
import logging

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


REQUIRED_COLUMNS = [
    "service_uid", "train_identity", "station_name", "station_crs",
    "origin_name", "destination_name", "scheduled_arr_time", "actual_arr_time",
    "scheduled_dep_time", "actual_dep_time", "operator_name",
    "service_date", "platform", "platform_changed", "cancelled", "cancel_reason"
]


def check_all_required_columns_present(data: DataFrame, required_columns=REQUIRED_COLUMNS) -> bool:
    """Checking if all columns required are present."""
    missing_columns = [
        col for col in required_columns if col not in data.columns]
    if missing_columns:
        logger.error("Missing columns: %s", missing_columns)
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}")
    logger.info("All required columns are present.")
    return True


if __name__ == "__main__":
    pass
