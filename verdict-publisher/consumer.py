"""
Kafka Consumer
Week 8 - CyBreach Validator
"""

import json

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from config import KAFKA_BROKER, CONSUMER_GROUP
from topics import VERDICT_TOPIC


class VerdictConsumer:
    """
    Kafka consumer for receiving verdict events.

    Uses a dedicated consumer group so Kafka can track:
    - Consumer membership
    - Partition assignments
    - Committed offsets
    - Consumer lag
    """

    def __init__(self):
        self.consumer = None

    def connect(self):
        """
        Connect to Kafka and subscribe to the verdict-events topic.
        """

        try:
            self.consumer = KafkaConsumer(
                VERDICT_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                group_id=CONSUMER_GROUP,

                # Start from earliest available message
                # when this consumer group has no committed offset.
                auto_offset_reset="earliest",

                # We will explicitly commit offsets.
                enable_auto_commit=False,

                value_deserializer=lambda message: json.loads(
                    message.decode("utf-8")
                )
            )

            print("=" * 50)
            print("Verdict Publisher Kafka Consumer Connected")
            print(f"Broker: {KAFKA_BROKER}")
            print(f"Topic: {VERDICT_TOPIC}")
            print(f"Consumer Group: {CONSUMER_GROUP}")
            print("=" * 50)

        except KafkaError as e:
            print(f"Kafka connection failed: {e}")
            self.consumer = None

    def consume(self):
        """
        Consume verdict events and manually commit offsets.
        """

        if self.consumer is None:
            print("Consumer is not connected.")
            return

        print("Listening for verdict events...")

        try:
            for message in self.consumer:

                print("\n" + "=" * 50)
                print("Verdict Event Received")
                print("=" * 50)

                print(f"Topic: {message.topic}")
                print(f"Partition: {message.partition}")
                print(f"Offset: {message.offset}")
                print(
                    f"Consumer Group: {CONSUMER_GROUP}"
                )

                print("\nEvent:")
                print(json.dumps(message.value, indent=4))

                # Commit only after successful processing.
                self.consumer.commit()

                print(
                    f"Offset {message.offset} committed successfully."
                )

        except KeyboardInterrupt:
            print("\nConsumer interrupted by user.")

        except KafkaError as e:
            print(f"Kafka consumer error: {e}")

        finally:
            self.close()

    def close(self):
        """
        Close Kafka consumer connection.
        """

        if self.consumer is not None:
            self.consumer.close()
            self.consumer = None

        print("Kafka consumer closed.")


if __name__ == "__main__":
    consumer = VerdictConsumer()

    consumer.connect()

    if consumer.consumer is not None:
        consumer.consume()