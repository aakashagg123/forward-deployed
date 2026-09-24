# ---
# name: event-producer
# description: Test producer for the loan-applications Kafka topic (event registry demo)
# kind: client
# phase: 07
# lesson: 04
# ---
"""Publish a test 'applicationReceived' event to the topic the engine's event
registry consumes. Requires kafka-python (pip install kafka-python) and a
local Kafka on :9092; everything engine-side is declarative (.channel/.event).
"""
import json
import sys
import uuid

from kafka import KafkaProducer     # the only non-stdlib import in this track

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode(),
)

event = {
    "applicationId": sys.argv[1] if len(sys.argv) > 1 else f"APP-{uuid.uuid4().hex[:6]}",
    "pan": "ABCDE1234F",
    "amount": 750_000.0,
    "channel": "partner-api",
}

producer.send("loan-applications", event)
producer.flush()
print("published:", event)
# Engine side, milliseconds later: the registry matches key 'applicationReceived',
# and the start event in the model creates a new loanOrigination instance with
# the payload as variables — no controller, no webhook, no glue service.
