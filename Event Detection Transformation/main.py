import os
from quixstreams import Application
from datetime import datetime
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

import uuid

i = uuid.uuid4()

app = Application(consumer_group="hard-braking-v1"+str(i), auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"], value_deserializer="string")
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# Filter items out without brake value.
# sdf = sdf[sdf.contains("Brake")]

# # Calculate hopping window of 1s with 200ms steps.
# sdf = sdf.apply(lambda row: row["Brake"]) \
#         .hopping_window(1000, 200).mean().final() 
        
# sdf.print()

def find_message(main_string):

    checks = [
        {"check": " error ", "message": "Error keyword detected"},
        {"check": " stopping ", "message": "Service stopping"},
        {"check": " shutdown ", "message": "Service shutdown detected"}
    ]

    print("------------------------------------------------------------------------")
    # print(main_string)
    
    j = json.loads(main_string)

    if "message" in j:
        msg = j["message"]
        print(msg)
        main_string_lower = msg.lower()
        for item in checks:
            if item["check"].strip().lower() in main_string_lower:
                return item["message"]
        return None

    print("++------------------------------------------------------------------------")


# Filter only windows where average brake force exceeded 50%.
# sdf = sdf[sdf["message"] != ""]
sdf = sdf.apply(func=find_message)

# sdf = sdf[find_message(sdf["message"], checks)]


# Create nice JSON alert message.
# sdf = sdf.apply(lambda row: {
#     "Timestamp": str(datetime.fromtimestamp(row["start"]/1000)),
#     "Alert": {
#         "Title": "Hard braking detected.",
#         "Message": "For last 1 second, average braking power was " + str(row["value"])
#     }
# })

# Print JSON messages in console.
sdf.print()

# Send the message to the output topic
# sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)