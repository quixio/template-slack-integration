import os
from quixstreams import Application
from datetime import datetime

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v15", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)
# sdf.filter(lambda msg: msg)

def tx_message(data):
    user = data['user']
    text = data['text']
    event_ts = float(data['event_ts'])  # Convert to float for datetime

    # Convert timestamp to human-readable format
    human_readable_time = datetime.fromtimestamp(event_ts).strftime('%Y-%m-%d %H:%M:%S')

    return {
        "timestamp": human_readable_time,
        "user": user,
        "message": text
    }


# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html
sdf = sdf.apply(tx_message)
sdf = sdf.apply(lambda row: print(row))

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)