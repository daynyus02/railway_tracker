"""Main file that contains the incidents ETL pipeline and lambda handler."""

import logging

from dotenv import load_dotenv

from extract_incidents import extract
from transform_incidents import transform
from load_incidents import load

logger = logging.getLogger()
logger.setLevel("DEBUG")


def run_etl() -> None:
    """Runs the incidents ETL Pipeline."""
    data = extract()
    transformed_data = transform(data)
    load(transformed_data)


def lambda_handler(event, context) -> dict:
    """AWS Lambda handler that runs the ETL pipeline."""
    load_dotenv()
    try:
        logger.info("Lambda triggered, running ETL.")
        run_etl()
        return {
            "statusCode": 200,
            "body": "Incidents ETL pipeline completed successfully."
        }
    except Exception as e:
        logger.error("ETL job failed.")
        return {
            "statusCode": 500,
            "body": f"ETL failed: {str(e)}"
        }
