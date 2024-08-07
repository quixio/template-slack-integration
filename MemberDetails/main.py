import os
from quixstreams import Application
from datetime import timedelta
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from uuid import uuid4
app = Application(consumer_group="transformation-v2"+str(uuid4()), auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

# sdf = (
#     sdf.tumbling_window(duration_ms=timedelta(hours=1))
#     .count()
#     .final()
# )

def fn(data):
    print("------------------")
    json_object = json.loads(json.dumps(data))
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

    print("++++++++++++++++++")
    print(f"{data['profile']['real_name']}")
    print(f"{data['profile']['display_name']}")
    print(f"{data['tz']}")

sdf = sdf.apply(fn)

# sdf = sdf.update(lambda row: print(row))

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)