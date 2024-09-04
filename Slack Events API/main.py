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

# Listens to incoming messages
@app.message("")
def message_hello(message, say):
    print(message)
    producer.produce(topic.name, json.dumps(message), "messages")

# handle message changed (someone edited their original message)
@app.event("message")
def handle_message_events(body, logger):
    producer.produce(topic.name, json.dumps(body), "messages")

# Start your app
if __name__ == "__main__":
    # SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    tkn = 'xapp-1-A07DQ9Z6VUK-7700610932480-109d43bdfc2f2a638bf5fc845c382ac466bb18ab32f122e448a05258cfb6597f'
    SocketModeHandler(app, tkn).start()