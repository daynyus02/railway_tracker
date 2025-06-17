"""Modules/Functions required to push information to station topics."""
from pandas import DataFrame
from datetime import timedelta
import boto3


def get_delayed_trains(api_train_data: DataFrame) -> DataFrame:
    """Returns a dataframe that contains only delayed trains."""

    api_train_data = api_train_data.dropna(
        subset=["scheduled_dep_time", "actual_dep_time"])

    delayed_trains_mask = (
        api_train_data["actual_dep_time"] >
        api_train_data["scheduled_dep_time"]
    )

    return api_train_data[delayed_trains_mask]


def filter_by_route(api_train_data: DataFrame, origin: str, destination: str) -> DataFrame:
    """Filters delayed trains for a specific route."""
    return api_train_data[
        api_train_data["origin_name"] == origin,
        api_train_data["destination_name"] == destination
    ]


def send_notification(api_train_data: DataFrame):
    sns_client = boto3.client("sns")
    delayed_trains = get_delayed_trains(api_train_data)

    paddington_to_bristol_route = filter_by_route(
        delayed_trains, "London Paddington", "Bristol Temple Meads")

    print(paddington_to_bristol_route)


if __name__ == "__main__":
    pass
