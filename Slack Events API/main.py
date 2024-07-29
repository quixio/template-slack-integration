import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from quixstreams import Application

quix_app = Application()
topic =  quix_app.topic(os.environ["output"])
producer = quix_app.get_producer()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("")
def message_hello(message, say):
    print(message)
    producer.produce(topic.name, json.dumps(message), "messages")

@app.event("message")
def handle_message_events(body, logger):
    print(body)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
