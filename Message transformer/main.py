import os
from quixstreams import Application
from datetime import datetime

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

import uuid
app = Application(consumer_group="transformation-v16"+str(uuid.uuid4()), auto_offset_reset="earliest")

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
        rtn['updated_text'] = data['event']['message']['text']
        rtn['client_msg_id'] = data['event']['message']['client_msg_id']
    else:
        # handle original messages
        rtn['user'] = data['user']
        rtn['text'] = data['text']
        rtn['msg_id'] = data['client_msg_id']
    
    event_ts = float(data['ts'])

    # Convert timestamp to human-readable format
    rtn['human_readable_time'] = datetime.fromtimestamp(event_ts).strftime('%Y-%m-%d %H:%M:%S')

    print(rtn)
    # return {
    #     "message_id": rtn['msg_id'],
    #     "timestamp": human_readable_time,
    #     "user": rtn['user'],
    #     "message": rtn['text']
    # }


# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html
sdf = sdf.apply(tx_message)
sdf = sdf.apply(lambda row: print(row))

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)