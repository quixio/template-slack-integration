import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from validate_email import validate_email

from quixstreams import Application

quix_app = Application()
topic =  quix_app.topic(os.environ["output"])
token_topic =  quix_app.topic(os.environ["token_messages"])
producer = quix_app.get_producer()

# Initializes your app with your bot token and socket mode handler
slack_app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@slack_app.command("/my-token")
def handle_some_command(ack, body, logger, say):

    msg = "Please try again and let us know your email address along with your request, so we can contact you if you win a prize."

    def is_valid_email(email):
        return validate_email(email)
        
    def validate_json(input, field_name):
        if not input.get(field_name):
            return f"Hi there! {msg}"
    
    val_error = validate_json(body, 'text')

    if val_error != None:
        say(val_error)
    else:
        email = input.get('text').strip()

        if is_valid_email(email):
            print("Valid email address")
            say(f"Hi! Thanks for requesting an affiliate token. We have emailed you a verification link.")

        else:
            print("Invalid email address")
            say(f"Hi! Thanks for requesting an affiliate token. {msg}")

            
        print(body)
        producer.produce(token_topic.name, json.dumps(body), "token_messages")
        
    ack()

# Listens to incoming messages
@slack_app.message("")
def message_hello(message, say):
    print(message)
    producer.produce(topic.name, json.dumps(message), "messages")

# handle message changed (someone edited their original message)
@slack_app.event("message")
def handle_message_events(body, logger):
    producer.produce(topic.name, json.dumps(body), "messages")

# Start your app
if __name__ == "__main__":
    print(os.environ["SLACK_APP_TOKEN"])
    socket_handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    socket_handler.start()