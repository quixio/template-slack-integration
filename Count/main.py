import os
from quixstreams import Application
from datetime import timedelta

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v242", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

sdf = (
    sdf.tumbling_window(duration_ms=timedelta(hours=1))
    .count()
    .final()
)
sdf.print()

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)