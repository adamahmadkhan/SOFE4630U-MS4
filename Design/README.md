# MS4 Smart Meter Microservices

This Design replaces the smart-meter Dataflow preprocessing with two
Python microservices running on GKE.

## Message flow

All stages use one Pub/Sub topic named smartMeterMS4.

- Producer publishes readings with stage="raw".
- FilterReading receives raw readings and removes records containing
  None in temperature, humidity, or pressure. Complete readings are
  published with stage="filtered".
- ConvertReading receives filtered readings, converts Celsius to
  Fahrenheit and kPa to psi, and publishes with stage="converted".
- A BigQuery subscription stores only converted readings.

Temperature conversion: F = C * 1.8 + 32.
Pressure conversion: psi = kPa / 6.895.
Humidity is unchanged. Valid zero values are preserved.

## Files

- producer.py: test readings and random smart-meter simulation.
- filter_reading/main.py: filters incomplete readings.
- convert_reading/main.py: converts the measurements.
- Each service folder contains its Dockerfile.
- design-deployments.json: Kubernetes deployments.

## Cloud resources

- Project: sofe4630u-ms1-509300
- Kubernetes namespace: ms4-design
- Topic: smartMeterMS4
- Filter subscription: ms4-filter-sub, stage="raw"
- Convert subscription: ms4-convert-sub, stage="filtered"
- BigQuery subscription: ms4-bigquery-sub, stage="converted"
- Destination table: MS4.ProcessedReadings
- BigQuery subscription uses the table schema.

The table fields are ID, time, profile_name, temperature, humidity,
pressure, and run_id. Stored temperature is Fahrenheit and pressure
is psi. The run_id identifies a producer run.

## Running the producer

Install google-cloud-pubsub in a Python virtual environment.
Set GOOGLE_APPLICATION_CREDENTIALS to a credential file outside
the repository.

Run python3 producer.py --test for six known test readings.
The expected result is three complete readings in BigQuery.
The test covers missing measurements, zeros, and negative temperature.

Run python3 producer.py --count 30 for random readings.

For the GKE services, credentials are mounted through a Kubernetes
Secret at runtime and are not included in the Docker images.

## Reference

Assignment and voting example:
https://github.com/MohammadYasserZaki/SOFE4630U-MS4
