"""Modules/Functions required to push information to station topics."""
import logging
from pandas import DataFrame
import boto3


logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def filter_by_route(delayed_train_data: DataFrame, origin: str, destination: str) -> DataFrame:
    """Filters delayed trains for a specific route."""
    filtered_route = delayed_train_data[
        (delayed_train_data["origin_name"] == origin) &
        (delayed_train_data["destination_name"] == destination)
    ]
    logging.info(
        "Filtered %s delayed train(s) for route: %s → %s.",
        len(filtered_route), origin, destination
    )
    return filtered_route


def send_notification(delayed_train_data: DataFrame) -> None:
    """Sends notification to specific route topics."""
    sns_client = boto3.client("sns")

    routes = [
        ("London Paddington", "Bristol Temple Meads")
    ]

    routes_to_crs = {
        "London Paddington": "PAD",
        "Bristol Temple Meads": "BRI"
    }

    for origin, destination in routes:
        logging.info("Filtering for %s -> %s", origin, destination)
        delayed_train_for_current_route = filter_by_route(
            delayed_train_data, origin, destination)

        if delayed_train_for_current_route.empty:
            logging.info(
                "No delays found for %s -> %s", origin, destination)
        else:
            message = [
                f"🚨Delayed Departures: {origin} -> {destination}🚨\n"
            ]

            for _, row in delayed_train_for_current_route.iterrows():
                station = (
                    f"Departing From: {row['station_name']}\n"
                    f"Scheduled: {row['scheduled_dep_time_api']}\n"
                    f"Actual: {row['actual_dep_time_api']}\n"
                    f"Delay: {row["delay_new"]} min\n"
                    f"Platform: {row.get('platform', 'N/A')}"
                )

                message.append(station)

            full_message = "\n\n".join(message)

            topic_name = f"c17-trains-delays-{routes_to_crs[origin]}-{routes_to_crs[destination]}"
            response = sns_client.create_topic(Name=topic_name)
            topic_arn = response["TopicArn"]

            sns_client.publish(
                TopicArn=topic_arn,
                Message=full_message,
                Subject=f"Delays: {origin} → {destination}"
            )

            logging.info("Published delay alert to SNS topic %s", topic_arn)
