from quixstreams import Application
from fastembed import TextEmbedding
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

targettable = os.environ['PG_TABLE']

app = Application(
    consumer_group="vectorsv1",
    auto_offset_reset="earliest",
    auto_create_topics=True,  # Quix app has an option to auto create topics
)

# Define input and ouput topics with JSON deserializer
input_topic = app.topic(os.environ['input'], value_deserializer="json")
output_topic = app.topic(os.environ['output'], value_serializer="json")

# This will trigger the model download and initialization
embedding_model = TextEmbedding()
print("The model BAAI/bge-small-en-v1.5 is ready to use.")

def simplify_data(row):

    # Creating a new dictionary that includes 'kind' and zips column names with values
    new_structure = {"kind": row["kind"],"table": row["table"]}
    new_structure.update({key: value for key, value in zip(row["columnnames"], row["columnvalues"])})

    # Optionally converting integers to strings
    new_structure["year"] = str(new_structure["year"])

    return new_structure


# Define the embedding function
def create_embeddings(row):

    # Values extracted from the JSON
    text = row["text"]
    msg_id = str(row["msg_id"])
    ts = str(row["ts"])
    user = str(row["user"])
    is_update = str(row["is_update"])

    # Create embeddings
    text_embedding = embedding_model.embed([text])  # Wrap in a list for batch processing
    client_msg_id_embedding = embedding_model.embed([msg_id])
    ts_embedding = embedding_model.embed([ts])
    user_embedding = embedding_model.embed([user])
    is_update_embedding = embedding_model.embed([is_update])

    # Combine embeddings into a single vector
    combined_embedding = text_embedding + client_msg_id_embedding + ts_embedding + user_embedding + is_update_embedding

    return combined_embedding

# Initialize a streaming dataframe based on the stream of messages from the input topic:
sdf = app.dataframe(topic=input_topic)

sdf = sdf.filter(lambda data: data["table"] == targettable)
sdf = sdf.update(lambda val: logger.info(f"Original data: {val}"))

sdf = sdf.apply(simplify_data)
sdf = sdf.update(lambda val: logger.info(f"Received update: {val}"))

# Trigger the embedding function for any new messages(rows) detected in the filtered SDF
sdf["embeddings"] = sdf.apply(create_embeddings, stateful=False)

# Update the timestamp column to the current time in nanoseconds
sdf["Timestamp"] = sdf.apply(lambda row: time.time_ns())

# Publish the processed SDF to a Kafka topic specified by the output_topic object.
sdf = sdf.to_topic(output_topic)

app.run(sdf)