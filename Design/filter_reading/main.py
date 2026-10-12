import json
import os
from google.cloud import pubsub_v1

PROJECT = os.environ["GCP_PROJECT"]
TOPIC = os.environ.get("TOPIC_NAME", "smartMeterMS4")
SUBSCRIPTION = os.environ.get("SUBSCRIPTION_ID", "ms4-filter-sub")

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(PROJECT, TOPIC)
subscription_path = subscriber.subscription_path(PROJECT, SUBSCRIPTION)


def callback(message):
    try:
        reading = json.loads(message.data.decode("utf-8"))
        measurements = ("temperature", "humidity", "pressure")

        if any(reading.get(field) is None for field in measurements):
            print(f"Dropped incomplete reading: {reading}", flush=True)
            message.ack()
            return

        publisher.publish(
            topic_path,
            json.dumps(reading).encode("utf-8"),
            stage="filtered"
        ).result(timeout=30)

        print(f"Passed complete reading: {reading}", flush=True)
        message.ack()

    except Exception as error:
        print(f"FilterReading error: {error}", flush=True)
        message.nack()


print(f"FilterReading listening on {subscription_path}", flush=True)

with subscriber:
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
