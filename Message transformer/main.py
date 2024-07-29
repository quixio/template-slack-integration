import os
from quixstreams import Application
from datetime import datetime
import uuid

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)
# sdf.filter(lambda msg: msg)

def tx_message(data):
    print("---------------")
    print(data)
    print("---------------")

    rtn = {}

    # handle message edits
    if 'event' in data and data['event'].get('type') == 'message' and data['event'].get('subtype') == 'message_changed':
        rtn['user'] = data['event']['message']['user']
        rtn['text'] = data['event']['message']['text']
        rtn['msg_id'] = data['event']['message']['client_msg_id']
        rtn['ts'] = float(data['event']['message']['ts'])
        rtn['is_update'] = True
    else:
        # handle original messages
        rtn['user'] = data['user']
        rtn['text'] = data['text']
        rtn['msg_id'] = data['client_msg_id']
        rtn['ts'] = float(data['ts'])
        rtn['is_update'] = False
        
    # Convert timestamp to human-readable format
    rtn['human_readable_time'] = datetime.fromtimestamp(int(rtn['ts'])).strftime('%Y-%m-%d %H:%M:%S')
    rtn['id'] = uuid.uuid4()
    return rtn


# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html
sdf = sdf.apply(tx_message)
sdf = sdf.apply(lambda row: print(row))

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)