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

    test_str = "geeksforgeeks"
    print("The original string is: ",test_str)
    res = "".join("".join(x) for x in zip(test_str[0::2].upper(), test_str[1::2].lower()))
    print("The alternate case string is : " + res)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()