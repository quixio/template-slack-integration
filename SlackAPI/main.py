from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import os
import json
import logging

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
slack_client = WebClient(token=os.environ.get("slack_token"))
logger = logging.getLogger(__name__)


# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

# this function loads the file and sends each row to the publisher
def get_data():

    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        return slack_client.users_list()

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """

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


    # create a pre-configured Producer object.
    with app.get_producer() as producer:
        # iterate over the data from the hardcoded dataset
        data = get_data()

        for member in result["members"]:
            print(member["real_name"])  # or use member["name"] if you prefer
            
        # print(data)
        # for row_data in data:
        #     print("------------------")
        #     print(row_data)

            # json_data = json.dumps(row_data)  # convert the row to JSON

            # publish the data to the topic
            # producer.produce(
            #     topic=topic.name,
            #     key=row_data['host'],
            #     value=json_data,
            # )

        print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")