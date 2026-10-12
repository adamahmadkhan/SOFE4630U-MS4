import argparse
import json
import os
import random
import time
import uuid
from pathlib import Path
from google.cloud import pubsub_v1

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
parser.add_argument("--count", type=int, default=30)
args = parser.parse_args()

if args.count < 1:
    parser.error("--count must be at least 1")

project = os.environ.get("GCP_PROJECT", "sofe4630u-ms1-509300")
topic = os.environ.get("TOPIC_NAME", "smartMeterMS4")
run_id = str(uuid.uuid4())
measurements = ("temperature", "humidity", "pressure")

if args.test:
    samples = [
        ("test_valid", 25, 50, 68.95),
        ("test_zero", 0, 0, 0),
        ("test_negative", -10, 60, 101.325),
        ("missing_temperature", None, 50, 100),
        ("missing_humidity", 20, None, 100),
        ("missing_pressure", 20, 50, None)
    ]

    rows = [
        {
            "profile_name": name,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure
        }
        for name, temperature, humidity, pressure in samples
    ]
else:
    rows = []
    for _ in range(args.count):
        reading = {
            "profile_name": random.choice(["boston", "denver", "losang"]),
            "temperature": round(random.uniform(-10, 40), 2),
            "humidity": round(random.uniform(20, 90), 2),
            "pressure": round(random.uniform(95, 105), 3)
        }

        if random.random() < 0.25:
            reading[random.choice(measurements)] = None

        rows.append(reading)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project, topic)
expected = 0

print(f"Run ID: {run_id}", flush=True)

for number, reading in enumerate(rows, start=1):
    reading["ID"] = number
    reading["time"] = int(time.time())
    reading["run_id"] = run_id

    if all(reading[field] is not None for field in measurements):
        expected += 1

    publisher.publish(
        topic_path,
        json.dumps(reading).encode("utf-8"),
        stage="raw"
    ).result(timeout=30)

    print(f"Published: {reading}", flush=True)
    time.sleep(0.5)

Path(__file__).with_name(".last_run_id").write_text(run_id)
print(f"Published records: {len(rows)}")
print(f"Expected stored records: {expected}")
