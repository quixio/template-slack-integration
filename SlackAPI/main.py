from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import os
import json
import logging
import time

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()
print(os.environ)
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
slack_client = WebClient(token=os.environ.get("slack_token"))
logger = logging.getLogger(__name__)

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """
    while True:
        slack_members = []
        # Call the users.list method using the WebClient
        try:
            result = slack_client.users_list()
            
            # Check if the response is ok
            if result["ok"]:
                # Loop through members and print their names
                slack_members = result["members"]
            else:
                print("Error: {}".format(result.get("error", "Unknown error")))

        except SlackApiError as e:
            logger.error("Error creating conversation: {}".format(e))
        
        if slack_members == []:
            print("No slack members")
        else:
            # create a pre-configured Producer object.
            with app.get_producer() as producer:
                
                def print_properties(obj, indent=0):
                    for key, value in obj.items():
                        print("  " * indent + f"{key}: {value}")
                        if isinstance(value, dict):
                            print_properties(value, indent + 1)

                for member in slack_members:
                    print_properties(member)

                    json_data = json.dumps(member)  # convert the row to JSON

                    # publish the data to the topic
                    producer.produce(
                        topic=topic.name,
                        key='slack_members',
                        value=json_data,
                    )
                    
                print("All rows published")
        
        time.sleep(14400) # sleep 4 hours


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")