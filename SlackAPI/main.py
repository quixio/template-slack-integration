from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import random
import os
import json
import logging

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
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
    # You probably want to use a database to store any user information ;)
    users_store = {}

    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        result = client.users_list()
        save_users(result["members"])

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


    # Put users into the dict
    def save_users(users_array):
        for user in users_array:
            # Key user info on their unique user ID
            user_id = user["id"]
            # Store the entire user object (you may not need all of the info)
            users_store[user_id] = user




def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """

    # create a pre-configured Producer object.
    with app.get_producer() as producer:
        # iterate over the data from the hardcoded dataset
        data_with_id = get_data()
        for row_data in data_with_id:

            json_data = json.dumps(row_data)  # convert the row to JSON

            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=row_data['host'],
                value=json_data,
            )

            # for more help using QuixStreams see docs:
            # https://quix.io/docs/quix-streams/introduction.html

        print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")