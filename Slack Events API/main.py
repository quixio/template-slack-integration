import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("#sarcasm")
def message_hello(message, say):
    msg = str(message["text"][8:])

    res = ""
    for idx in range(len(msg)):
        if not idx % 2:
            res = res + msg[idx].upper()
        else:
            res = res + msg[idx].lower()
            
    # say(f"{message['text']}")
    # print("rx message" + message["text"])
    print(msg)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()