import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from validate_email import validate_email
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from quixstreams import Application

quix_app = Application()
topic =  quix_app.topic(os.environ["output"])
token_topic =  quix_app.topic(os.environ["token_messages"])
producer = quix_app.get_producer()

# Initializes your app with your bot token and socket mode handler
slack_app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, password):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Create server object with SSL option
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)

    # Perform operations via server
    server.login(login, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

@slack_app.command("/my-token")
def handle_some_command(ack, body, logger, say):

    # Example usage
    # subject = "Test Email"
    # body = "This is a test email."
    # to_email = "recipient@example.com"
    from_email = "devrel@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    login = os.environ["gmail_username"]
    password = os.environ["gmail_password"]

    msg = "Please try again and let us know your email address along with your request, so we can contact you if you win a prize"

    def extract_email(text):
        match = re.search(r'<mailto:(.*?)(?:\|.*?)?>', text)
        return match.group(1) if match else text

    def is_valid_email(text):
        email = extract_email(text).strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def validate_json(input, field_name):
        if not input.get(field_name):
            return f"Hi there! {msg}."
    
    val_error = validate_json(body, 'text')

    if val_error != None:
        say(val_error)
    else:
        email = body.get('text').strip()
        
        # if is_valid_email(email):
        #     print("Invalid email address")
        #     say(f"Hi! Thanks for requesting an affiliate token. {msg}.")
        # else:
        #     print("Valid email address")
        #     say(f"Hi! Thanks for requesting an affiliate token. We have emailed you a verification link.")
        #     producer.produce(token_topic.name, json.dumps(body), "token_request_verification")

        say("Okay.. I'll assume your email address is valid.. sending you an email!")
        send_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, password)
        
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