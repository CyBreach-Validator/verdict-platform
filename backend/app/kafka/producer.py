"""Kafka producer for the plan's v2.0 verdict topics.

N-D9: every publish here runs `validate_verdict_event()` first, so a payload
that drifted from the frozen contract fails at the bus instead of shipping
silently. The previous version accepted any `dict` and sent it.
"""

import json
import logging

from app.contracts.verdict_event import validate_verdict_event
from app.kafka.config import (
    GAP_CLOSED_TOPIC,
    KAFKA_SERVER,
    PLAN_TOPICS,
    VERDICT_TOPIC,
)

logger = logging.getLogger(__name__)

producer = None


def _get_producer():
    """Lazily build the producer.

    Import-time construction was a problem in two ways: it blocked app startup
    for the broker's full connect timeout whenever Kafka was absent, and it made
    the module unimportable in a test environment with no broker. Delta only
    produces, and a verdict that cannot reach the bus must not stop the verdict
    from being stored and returned over REST.
    """

    global producer

    if producer is not None:
        return producer

    try:
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        logger.info("Connected to Kafka at %s", KAFKA_SERVER)
    except Exception as exc:  # noqa: BLE001 - broker absence must not be fatal
        logger.warning("Kafka is not available (%s); publishing is disabled", exc)
        producer = None

    return producer


def _publish(topic: str, payload: dict, description: str) -> bool:
    """Validate against the frozen contract, then send. Returns success."""

    # N-D5: the manifest is the registry of the bus. Checking the topic here
    # means a typo or a topic nobody declared fails at the send site instead of
    # silently writing to a partition no consumer in the run plan subscribes to.
    if topic not in PLAN_TOPICS:
        raise ValueError(
            f"{topic!r} is not in the plan's topic manifest: {PLAN_TOPICS}"
        )

    # N-D9: fail loudly on a contract violation. This is a programming error,
    # not a broker problem, so it is allowed to propagate to the caller.
    validate_verdict_event(payload)

    active = _get_producer()

    if active is None:
        logger.warning("Kafka producer not initialized. Skipping %s", description)
        return False

    try:
        from kafka.errors import KafkaError

        try:
            active.send(topic, payload)
            active.flush()
            logger.info("Published %s to %s", description, topic)
            return True
        except KafkaError as exc:
            logger.warning("Failed to publish %s to %s: %s", description, topic, exc)
            return False
    except ImportError:
        logger.warning("kafka-python is not installed; skipping %s", description)
        return False


def publish_verdict(verdict: dict):
    return _publish(VERDICT_TOPIC, verdict, "verdict")


def publish_corrected_verdict(verdict: dict):
    """Publish a corrected verdict event to Kafka."""

    return _publish(VERDICT_TOPIC, verdict, "corrected verdict")


def publish_gap_closed_event(event: dict):
    """Publish a gap-closed event when a previously missed verdict becomes
    detected after re-validation."""

    return _publish(GAP_CLOSED_TOPIC, event, "gap-closed event")
