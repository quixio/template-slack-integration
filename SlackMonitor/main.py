from quixstreams import Application
import os
import json
import logging
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_client = WebClient(token=os.environ.get("slack_token"))
logger = logging.getLogger(__name__)

app = Application(consumer_group="data_source", auto_create_topics=True)
topic_name = os.environ["output"]
topic = app.topic(topic_name)

def main():
    """
    Monitor all Slack channels and publish messages to Kafka
    """
    while True:
        try:
            # Call the conversations.list method to get all channels
            channels_result = slack_client.conversations_list()
            if not channels_result["ok"]:
                print("Error: {}".format(channels_result.get("error", "Unknown error")))
                continue

            channels = channels_result["channels"]

            # Iterate over each channel to fetch messages
            for channel in channels:
                channel_id = channel["id"]
                messages_result = slack_client.conversations_history(channel=channel_id)

                if not messages_result["ok"]:
                    print("Error: {}".format(messages_result.get("error", "Unknown error")))
                    continue

                messages = messages_result["messages"]

                # Create a pre-configured Producer object
                with app.get_producer() as producer:
                    for message in messages:
                        message_data = {
                            "timestamp": message.get("ts"),
                            "text": message.get("text"),
                            "link": f"https://slack.com/app_redirect?channel={channel_id}&message_ts={message.get('ts')}"
                        }

                        json_data = json.dumps(message_data)
                        print(json_data)
                        # # Publish the data to the topic
                        # producer.produce(
                        #     topic=topic.name,
                        #     key='slack_messages',
                        #     value=json_data,
                        # )

                    print(f"Messages from channel {channel_id} published")

        except SlackApiError as e:
            logger.error("Error fetching messages: {}".format(e))

        time.sleep(14400)  # sleep 4 hours

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")