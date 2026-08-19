"""
Kafka Consumer Monitoring
Week 9 - CyBreach Validator

Provides:
- Consumer group offset tracking
- Partition-level lag monitoring
- Total lag calculation
- Lag threshold alerting
"""

from kafka import KafkaConsumer, TopicPartition

from config import KAFKA_BROKER, CONSUMER_GROUP
from topics import VERDICT_TOPIC


# Alert when total consumer lag reaches this value.
LAG_ALERT_THRESHOLD = 10


class KafkaConsumerMonitor:
    """
    Provides consumer offset and lag information
    for the Verdict Publisher consumer group.
    """

    def __init__(self):
        self.consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BROKER,
            group_id=CONSUMER_GROUP,
            enable_auto_commit=False
        )

        self.consumer.subscribe([VERDICT_TOPIC])

    def get_status(self):
        """
        Return Kafka consumer offset and lag information.
        """

        partitions = self.consumer.partitions_for_topic(
            VERDICT_TOPIC
        )

        if not partitions:
            return {
                "group_id": CONSUMER_GROUP,
                "topic": VERDICT_TOPIC,
                "partitions": [],
                "total_lag": 0,
                "lag_alert": False,
                "lag_threshold": LAG_ALERT_THRESHOLD
            }

        topic_partitions = [
            TopicPartition(
                VERDICT_TOPIC,
                partition
            )
            for partition in partitions
        ]

        # Force assignment so Kafka can provide
        # consumer position information.
        self.consumer.poll(timeout_ms=1000)

        results = []

        for tp in topic_partitions:

            committed_offset = self.consumer.committed(tp)

            end_offsets = self.consumer.end_offsets([tp])

            latest_offset = end_offsets.get(tp, 0)

            if committed_offset is None:
                current_offset = None
                lag = latest_offset
            else:
                current_offset = committed_offset
                lag = max(
                    latest_offset - committed_offset,
                    0
                )

            results.append({
                "partition": tp.partition,
                "current_offset": current_offset,
                "latest_offset": latest_offset,
                "lag": lag
            })

        total_lag = sum(
            item["lag"]
            for item in results
            if item["lag"] is not None
        )

        lag_alert = total_lag >= LAG_ALERT_THRESHOLD

        return {
            "group_id": CONSUMER_GROUP,
            "topic": VERDICT_TOPIC,
            "partitions": results,
            "total_lag": total_lag,
            "lag_alert": lag_alert,
            "lag_threshold": LAG_ALERT_THRESHOLD
        }

    def check_lag_alert(self):
        """
        Check consumer lag and print an operational alert
        when the configured threshold is exceeded.
        """

        status = self.get_status()

        if status["lag_alert"]:
            print(
                "\nWARNING: Kafka consumer lag alert!"
            )

            print(
                f"Consumer group: {status['group_id']}"
            )

            print(
                f"Total lag: {status['total_lag']}"
            )

            print(
                f"Threshold: {status['lag_threshold']}"
            )

        else:
            print(
                f"Kafka consumer lag healthy: "
                f"{status['total_lag']}"
            )

        return status

    def close(self):
        """
        Close Kafka consumer connection.
        """

        self.consumer.close()


if __name__ == "__main__":

    monitor = KafkaConsumerMonitor()

    try:
        status = monitor.check_lag_alert()

        print("=" * 60)
        print("Kafka Consumer Monitoring")
        print("=" * 60)

        print(f"Group: {status['group_id']}")
        print(f"Topic: {status['topic']}")

        print("\nPartitions:")

        for partition in status["partitions"]:
            print(
                f"Partition {partition['partition']} | "
                f"Current Offset: {partition['current_offset']} | "
                f"Latest Offset: {partition['latest_offset']} | "
                f"Lag: {partition['lag']}"
            )

        print(
            f"\nTotal Lag: {status['total_lag']}"
        )

        print(
            f"Lag Alert: {status['lag_alert']}"
        )

    finally:
        monitor.close()