import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.kafka.config import VERDICT_TOPIC, GAP_CLOSED_TOPIC


producer = None


try:
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    print("✅ Connected to Kafka")

except Exception as e:
    print(f"⚠️ Kafka is not available: {e}")


def publish_verdict(verdict: dict):
    if producer:
        try:
            producer.send(VERDICT_TOPIC, verdict)
            producer.flush()
            print("✅ Verdict published to Kafka")

        except KafkaError as e:
            print(f"❌ Failed to publish verdict: {e}")

    else:
        print("⚠️ Kafka producer not initialized. Skipping publish.")


def publish_corrected_verdict(verdict: dict):
    """
    Publish a corrected verdict event to Kafka.
    """

    if producer:
        try:
            producer.send(VERDICT_TOPIC, verdict)
            producer.flush()
            print("✅ Corrected verdict published to Kafka")

        except KafkaError as e:
            print(f"❌ Failed to publish corrected verdict: {e}")

    else:
        print("⚠️ Kafka producer not initialized.")


def publish_gap_closed_event(event: dict):
    """
    Publish a gap-closed event when a previously missed
    verdict becomes detected after re-validation.
    """

    if producer:
        try:
            producer.send(GAP_CLOSED_TOPIC, event)
            producer.flush()
            print("✅ Gap-closed event published to Kafka")

        except KafkaError as e:
            print(f"❌ Failed to publish gap-closed event: {e}")

    else:
        print("⚠️ Kafka producer not initialized. Skipping gap-closed event.")