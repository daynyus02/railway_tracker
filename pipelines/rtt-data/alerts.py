"""Modules/Functions required to push information to station topics."""
import logging
from datetime import datetime, date
from pandas import DataFrame
from datetime import timedelta
import boto3


logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def get_delayed_trains(api_train_data: DataFrame) -> DataFrame:
    """Returns a dataframe that contains only delayed trains."""
    delayed_trains_mask = (
        api_train_data["actual_dep_time"] >
        api_train_data["scheduled_dep_time"]
    )
    delayed_trains = api_train_data[delayed_trains_mask]
    logging.info(f"Found {len(delayed_trains)} delayed train(s).")
    return delayed_trains


def filter_by_route(api_train_data: DataFrame, origin: str, destination: str) -> DataFrame:
    """Filters delayed trains for a specific route."""
    filtered_route = api_train_data[
        (api_train_data["origin_name"] == origin) &
        (api_train_data["destination_name"] == destination)
    ]
    logging.info(
        f"Filtered {len(filtered_route)} delayed train(s) for route: {origin} → {destination}.")
    return filtered_route


def send_notification(api_train_data: DataFrame) -> None:
    """Sends notification to specific route topics."""
    sns_client = boto3.client("sns")

    logging.info("Filtering delayed trains...")
    delayed_trains = get_delayed_trains(api_train_data)

    routes = [
        ("London Paddington", "Bristol Temple Meads")
    ]

    routes_to_crs = {
        "London Paddington": "PAD",
        "Bristol Temple Meads": "BRI"
    }

    for origin, destination in routes:
        logging.info(f"Filtering for {origin} -> {destination}")
        delayed_train_for_current_route = filter_by_route(
            delayed_trains, origin, destination)

        if delayed_train_for_current_route.empty:
            logging.info(
                f"No delays found for {origin} -> {destination} route")
        else:
            message = [
                f"🚨Delayed Departures: {origin} -> {destination}🚨\n"
            ]

            for _, row in delayed_train_for_current_route.iterrows():
                scheduled = datetime.combine(
                    date.today(), row["scheduled_dep_time"])
                actual = datetime.combine(date.today(), row["actual_dep_time"])
                delay_minutes = int((actual - scheduled).total_seconds() // 60)

                station = (
                    f"{row['station_name']}\n"
                    f"Scheduled: {row['scheduled_dep_time']}\n"
                    f"Actual: {row['actual_dep_time']}\n"
                    f"Delay: {delay_minutes} min\n"
                    f"Platform: {row.get('platform', 'N/A')}"
                )

                message.append(station)

            full_message = "\n".join(message)

            topic_name = f"c17-trains-delays-{routes_to_crs[origin]}-{routes_to_crs[destination]}"
            response = sns_client.create_topic(Name=topic_name)
            topic_arn = response["TopicArn"]

            sns_client.publish(
                TopicArn=topic_arn,
                Message=full_message,
                Subject=f"Delays: {origin} → {destination}"
            )

            logging.info(f"Published delay alert to SNS topic {topic_arn}")
