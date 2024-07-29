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
    test_str = str(message["text"][8:])

    res = [ele.upper() if not idx % 2 else ele.lower()
        for idx, ele in enumerate(test_str)]
    res = "".join(res)
            
    # say(f"{message['text']}")
    # print("rx message" + message["text"])
    print(res)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()