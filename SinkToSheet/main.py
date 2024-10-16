import logging
from quixstreams import Application
from uuid import uuid4
from datetime import timedelta
import pygsheets

# incomming data
# {
#   "start": 1729085226000,
#   "end": 1729085227000,
#   "value": 510
# }

def initializer_fn(msg):
    count = msg["value"]

    return {
        "count": count
    }


def reducer_fn(summary, msg):
    count = msg["value"]

    return {
        "count": count
    }


def main():
    app = Application(
        broker_address="localhost:9092",
        loglevel="DEBUG",
        consumer_group="weather_to_google",
        auto_offset_reset="earliest",
    )

    input_topic = app.topic("weather_data_demo")

    sdf = app.dataframe(input_topic)

    # sdf = sdf.group_into_hourly_batches(...)
    sdf = sdf.tumbling_window(duration_ms=timedelta(hours=12))

    # sdf = sdf.summarize_that_hour(...)
    sdf = sdf.reduce(
        initializer=initializer_fn,
        reducer=reducer_fn,
    )
    sdf = sdf.final()

    sdf = sdf.update(lambda msg: logging.debug("Got: %s", msg))

    google_api = pygsheets.authorize()
    workspace = google_api.open("Public Slack UserCount")
    sheet = workspace[0]
        sheet.update_values(
        "A1",
        [
            ["User Count"]
        ],
    )

    def to_google(msg):
        sheet.insert_rows(
            1,
            values=[
                msg["value"]["user_count"]
            ],
        )

    sdf = sdf.apply(to_google)

    app.run(sdf)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main()