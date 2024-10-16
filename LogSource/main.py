from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import random
import os
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)


# this function loads the file and sends each row to the publisher
def get_data():
    import requests

def stream_logs(deployment_id, base_url, headers=None):
    url = f"{base_url}/deployments/{deployment_id}/logs/stream"
    
    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()  # Check for HTTP errors
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))

def main():

    # Example usage
    deployment_id = "daff9f81-8d8a-4ae8-bb48-3676fb4e05e8"
    base_url = "https://portal-api.platform.quix.io"
    headers = {
        "Authorization": "Bearer " + os.environ["token"]
    }

    stream_logs(deployment_id, base_url, headers)


    # # create a pre-configured Producer object.
    # with app.get_producer() as producer:
    #     # iterate over the data from the hardcoded dataset
    #     data_with_id = get_data()
    #     for row_data in data_with_id:

    #         json_data = json.dumps(row_data)  # convert the row to JSON

    #         # publish the data to the topic
    #         producer.produce(
    #             topic=topic.name,
    #             key=row_data['host'],
    #             value=json_data,
    #         )

    #         # for more help using QuixStreams see docs:
    #         # https://quix.io/docs/quix-streams/introduction.html

    #     print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")