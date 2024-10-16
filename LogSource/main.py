from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import os
import requests

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

def handle_message(deployment_id, message):
    # create a pre-configured Producer object.
    with app.get_producer() as producer:
        # publish the data to the topic
        producer.produce(
            topic=topic.name,
            key=deployment_id.encode('utf-8'),
            value=message,
        )
        print("All rows published")

def stream_logs(deployment_id, base_url, message_handler, headers=None):
    url = f"{base_url}/deployments/{deployment_id}/logs/stream"
    
    while True:
        try:
            print("Checking deployment logs availability...")
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()  # Check for HTTP errors
                print("Deployment logs available. Streaming logs...")
                for line in response.iter_lines():
                    if line:
                        print(line.decode('utf-8'))
                        message_handler(deployment_id, {"code": 0, "message": line.decode('utf-8')})
        except requests.exceptions.RequestException as e:
            print(f"Error accessing logs: {e}")
            message_handler(deployment_id, {"code": 1, "message": "Deployment is offline"})
        except KeyboardInterrupt:
            print("Exiting.")
            break

def main():
    # Example usage
    deployment_id = os.environ["deployment_id"]
    base_url = "https://portal-api.platform.quix.io"
    headers = {
        "Authorization": "Bearer " + os.environ["token"]
    }

    stream_logs(deployment_id, base_url, handle_message, headers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")