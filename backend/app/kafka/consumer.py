import json
from kafka import KafkaConsumer
from app.kafka.config import EVIDENCE_TOPIC

from app.database.database import SessionLocal
from app.services.rule_service import validate_uploaded_rule

consumer = KafkaConsumer(
    EVIDENCE_TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="validator-group-test",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("✅ Kafka Consumer started...")

db = SessionLocal()

for message in consumer:
    try:
        event = message.value

        print(f"Received Event: {event}")

        rule_id = event["rule_id"]
        event_data = event["event"]

        result = validate_uploaded_rule(
            db=db,
            rule_id=rule_id,
            event=event_data
        )

        print("Validation Result:", result)

    except Exception as e:
        print("Error:", e)
