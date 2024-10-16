import logging
from quixstreams import Application
from uuid import uuid4
from datetime import timedelta
import pygsheets
import os
import requests

# incomming data
# {
#   "start": 1729085226000,
#   "end": 1729085227000,
#   "value": 510
# }

from dotenv import load_dotenv
load_dotenv()

def get_client_secret():
    # URL of the publicly accessible blob
    blob_url = os.environ["google_auth_secret_url"]

    # Fetch the client_secret.json from Azure Blob Storage
    response = requests.get(blob_url)
    response.raise_for_status()  # Ensure the request was successful

    # Save the content to a local file
    with open("client_secret.json", "wb") as f:
        f.write(response.content)


def initializer_fn(msg):
    print(msg)
    count = msg["used_percent"]

    return {
        "count": count
    }


def reducer_fn(summary, msg):
    count = msg["used_percent"]

    return {
        "count": count
    }


def main():
    app = Application(
        loglevel="DEBUG",
        consumer_group="slack_users_v2",
        auto_offset_reset="earliest",
    )

    input_topic = app.topic(os.environ["input"])

    sdf = app.dataframe(input_topic)

    sdf = sdf.update(lambda msg: logging.debug("Got: %s", msg))

    google_api = pygsheets.authorize(service_file='client_secret.json')

    sheet_title="Public Slack User Count NEW"

    workspace = google_api.open(sheet_title)
    sheet = workspace[0]
    sheet.update_values(
        "A1",
        [
            ["Time", "User Count"]
        ],
    )

    def to_google(msg):
        print(msg)
        sheet.insert_rows(
            1,
            values=[
                str(msg)
            ],
        )

    sdf = sdf.apply(to_google)

    app.run(sdf)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    get_client_secret()
    main()