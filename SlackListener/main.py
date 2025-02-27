import os
import json
import logging
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from quixstreams import Application
import time

load_dotenv()

# Initialize Slack clients
slack_client = WebClient(token=os.environ.get("slack_bot_token"))
socket_mode_client = SocketModeClient(app_token=os.environ.get("slack_app_token"))

# Initialize Quix Streams application
app = Application(consumer_group="data_source", auto_create_topics=True)
topic_name = os.environ["output"]
topic = app.topic(topic_name)

logger = logging.getLogger(__name__)

def get_user_name(user_id):
    try:
        # print(user_id)
        response = slack_client.users_info(user=user_id)
        # print(response)
        if response["ok"]:
            return response["user"]["name"]
    except SlackApiError as e:
        logger.error(f"Error fetching user info: {e}")
    return "Unknown User"

def handle_message_events(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api" and req.payload["event"]["type"] == "message":
        event = req.payload["event"]
        channel_id = event.get("channel")
        message_ts = event.get("ts")
        message_text = event.get("text")
        user_id = event.get("user")
        user_name = get_user_name(user_id)

        # print(user_id)
        # print(user_name)


        message_data = {
            "timestamp": message_ts,
            "text": message_text,
            "link": f"https://slack.com/app_redirect?channel={channel_id}&message_ts={message_ts}"
        }

        json_data = json.dumps(message_data)
        print(json_data)
        # # Publish the data to the topic
        # with app.get_producer() as producer:
        #     producer.produce(
        #         topic=topic.name,
        #         key='slack_messages',
        #         value=json_data,
        #     )

        print(f"Message from channel {channel_id} published")

        # Acknowledge the request
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

def main():
    socket_mode_client.socket_mode_request_listeners.append(handle_message_events)
    socket_mode_client.connect()
    
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")