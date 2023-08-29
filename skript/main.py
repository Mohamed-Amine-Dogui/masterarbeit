import os
import glob
import time
import boto3
import logging
from datetime import datetime
from collections import deque


def setup_logging():
    logging.basicConfig(
        filename="main_setup.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def check_database_existence(timestream_client, database_name):
    try:
        timestream_client.describe_database(DatabaseName=database_name)
        logging.info(f"Database {database_name} already exists.")
        return True
    except timestream_client.exceptions.ResourceNotFoundException:
        logging.info(f"Database {database_name} does not exist.")
        return False
    except Exception as e:
        logging.error("Error checking database existence: %s", e)
        return False


def create_database(timestream_client, database_name):
    try:
        timestream_client.create_database(DatabaseName=database_name)
        logging.info(f"Database {database_name} successfully created.")
        return True
    except timestream_client.exceptions.ConflictException:
        logging.info(f"Database {database_name} already exists.")
        return False
    except Exception as e:
        logging.error("Error creating database: %s", e)
        return False


def check_table_existence(timestream_client, database_name, table_name):
    try:
        timestream_client.describe_table( DatabaseName=database_name, TableName=table_name )
        logging.info( f"Table {table_name} in database {database_name} already exists.")
        return True
    except timestream_client.exceptions.ResourceNotFoundException:
        logging.info( f"Table {table_name} in database {database_name} does not exist.")
        return False
    except Exception as e:
        logging.error("Error checking table existence: %s", e)
        return False


def create_table(timestream_client, database_name, table_name):
    retention_properties = {
        "MemoryStoreRetentionPeriodInHours": 1,
        "MagneticStoreRetentionPeriodInDays": 1,
    }
    try:
        timestream_client.create_table(
            DatabaseName=database_name,
            TableName=table_name,
            RetentionProperties=retention_properties,
        )
        logging.info(f"Table {table_name} successfully created.")
        return True
    except timestream_client.exceptions.ConflictException:
        logging.info(f"Table {table_name} exists in database {database_name}. Skipping table creation.")
        return False
    except Exception as e:
        logging.error("Error creating table: %s", e)
        return False


def read_temperature(sensor_id):
    try:
        # Path to the sensor data
        sensor_path = f"/sys/bus/w1/devices/{sensor_id}/w1_slave"

        # Read the raw data from the sensor file
        with open(sensor_path, "r") as sensor_file:
            lines = sensor_file.readlines()

        # Check if the data has been read successfully
        if "YES" not in lines[0]:
            raise Exception("Error reading sensor data")

        # Extract temperature from the data
        temperature_data = lines[1].split(" ")[9]
        temperature = float(temperature_data[2:]) / 1000.0

        return temperature

    except Exception as e:
        print("Error reading temperature:", e)
        return None


def find_sensor_id():
    # Sensor folder to search for DS18B20 sensors
    sensor_folder = "/sys/bus/w1/devices/"

    # Get a list of all DS18B20 sensors connected
    sensor_list = glob.glob(sensor_folder + "28-*")

    if not sensor_list:
        print("No DS18B20 sensors found.")
        return None

    # Find the first sensor ID that starts with "28-"
    sensor_id = next(
        (
            os.path.basename(sensor_path)
            for sensor_path in sensor_list
            if os.path.basename(sensor_path).startswith("28-")
        ),
        None,
    )
    return sensor_id


def calculate_average(temp_list, window_size):
    # Create a deque to store temperature readings for moving average
    temperature_readings = deque(temp_list, maxlen=window_size)

    # Exclude values of 0 and 85 from the list
    valid_values = [temp for temp in temperature_readings if temp != 0 and temp != 85]

    # Calculate the average of the valid values
    if valid_values:
        return sum(valid_values) / len(valid_values)
    else:
        return None


def send_sns_alert(sns_client, message):
    sns_topic_arn = "arn:aws:sns:eu-west-1:683603511960:SensorTopic"
    try:
        # Publish the message to the SNS topic
        response = sns_client.publish(TopicArn=sns_topic_arn, Message=message)
        print(f"Message sent successfully with MessageId: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending message: {e}")


def main():
    region_name = "eu-west-1"
    database_name = "db_sensor"
    table_name = "temp_evolution"
    alert_limit = 35.0
    alert_sent = False

    setup_logging()

    # Create a Timestream client
    timestream_client = boto3.client("timestream-write", region_name=region_name)

    # Create an SNS client
    sns_client = boto3.client("sns", region_name=region_name)

    if not check_database_existence(timestream_client, database_name):
        if not create_database(timestream_client, database_name):
            return

    if not check_table_existence(timestream_client, database_name, table_name):
        if not create_table(timestream_client, database_name, table_name):
            return

    # Create a deque to store temperature readings for moving average
    window_size = 5
    temperature_readings = deque(maxlen=window_size)

    while True:
        sensor_id = find_sensor_id()
        if sensor_id is not None:
            temperature = read_temperature(sensor_id)
            if temperature is not None:
                if temperature != 0 and temperature != 85:
                    print(f"Sensor {sensor_id}: Temperature: {temperature:.2f}°C")
                    temperature_readings.append(temperature)
                    try:
                        current_timestamp = datetime.now()
                        record = {
                            "Dimensions": [
                                {"Name": "SensorId", "Value": sensor_id},
                                {"Name": "Measurement", "Value": "Temperature"},
                            ],
                            "MeasureName": "temperature",
                            "MeasureValue": str(temperature),
                            "MeasureValueType": "DOUBLE",
                            "Time": str(
                                int(current_timestamp.timestamp() * 1000)
                            ),  # Convert to milliseconds
                        }

                        # Write the record to Timestream
                        timestream_client.write_records(
                            DatabaseName=database_name,
                            TableName=table_name,
                            Records=[record],
                        )
                        print(
                            f"Sensor {sensor_id}: Temperature: {temperature:.2f}°C - Written to Timestream"
                        )

                        # Check if the temperature exceeds the threshold for sending an alert
                        if temperature > alert_limit and not alert_sent:
                            message = f"Achtung! Grenzwert von {alert_limit} °C überschritten. Temperatur erreicht: {temperature:.2f}°C"
                            send_sns_alert(sns_client, message)
                            alert_sent = True
                        elif temperature <= alert_limit:
                            alert_sent = False

                    except Exception as e:
                        print("Error writing to Timestream:", e)

        # Wait for 1 second before reading again
        time.sleep(1)


if __name__ == "__main__":
    main()
