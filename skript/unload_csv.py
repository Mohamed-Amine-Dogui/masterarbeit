import boto3
from datetime import datetime
import logging
from logging import Logger

logger: Logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def setup_logging():
    logging.basicConfig(
        filename='unload_csv_setup.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def execute_timestream_unload_query(client, unload_query):
    try:
        response = client.query(QueryString=unload_query)
    except client.exceptions.ValidationException as e:
        logger.debug("Validation Exception:", e)
        raise
    except Exception as e:
        logger.debug("An error occurred:", e)
        raise


def main():

    setup_logging()

    target_s3_bucket = "sensor-daily-report-bucket"
    s3_prefix = datetime.now().strftime("%Y-%m-%d")

    timestream_client = boto3.client("timestream-query", region_name="eu-west-1")

    query_view = (
        "SELECT * FROM db_sensor.temp_evolution WHERE time >= ago(1d) ORDER BY time DESC"
    )

    unload_query = (
        f"UNLOAD ({query_view}) "
        f"TO 'S3://{target_s3_bucket}/{s3_prefix}'"
        f" WITH (format='CSV', compression='NONE') "
    )

    try:
        execute_timestream_unload_query(timestream_client, unload_query)

    except timestream_client.exceptions.ValidationException as e:
        logger.debug("An Exception occurred:", e)
        raise

    except Exception as e:
        logger.debug("An Exception occurred:", e)
        raise

if __name__ == "__main__":
    main()
