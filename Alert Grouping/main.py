import os
from quixstreams import Application
from datetime import timedelta

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

import uuid
i = str(uuid.uuid4())

app = Application(consumer_group="transformation-v" + i, auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)
sdf.print()
def initializer_fn(msg):
    # Initialize the state for the window
    return {
        "count": 0,
        "messages": []
    }

def reducer_fn(summary, msg):
    if msg is not None:
        print("--")
        print(msg)
        print("__")

        # Update the state with the new message
        summary["count"] += 1
        summary["messages"].append(msg["message"])
    return summary

# Define a 10-minute tumbling window
sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=5))

# Apply the initializer and reducer functions
sdf = sdf.reduce(
    initializer=initializer_fn,
    reducer=reducer_fn
)
sdf = sdf.final()
sdf = sdf.update(lambda x: print(x))
# sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)