"""
Plan Section 5 "Message Bus Topics" -- the one shared topic manifest.

Every producer and consumer in Pod Delta resolves topic names from here so
there is a single bus contract. The broker is injected via `KAFKA_BOOTSTRAP_SERVERS`
(defaulting to the local hybrid-run broker on 9092) rather than hardcoded in
each module.
"""

import os

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# --- Plan Section 5 topics -------------------------------------------------

EVIDENCE_TOPIC = "cybreach.evidence.v1"
VERDICT_TOPIC = "cybreach.verdicts.v2"
GAP_CLOSED_TOPIC = "cybreach.gap_closed.v2"
REVALIDATION_TOPIC = "cybreach.revalidation.v1"
CONNECTOR_HEALTH_TOPIC = "cybreach.connector.health.v1"

# Declared here so the manifest is the single place a topic name appears,
# even though the Validation Engine (Pod Beta) is the owner of the evidence
# subscription and the Re-Validation Service (Pod Gamma) owns revalidation.
PLAN_TOPICS = (
    EVIDENCE_TOPIC,
    VERDICT_TOPIC,
    GAP_CLOSED_TOPIC,
    REVALIDATION_TOPIC,
    CONNECTOR_HEALTH_TOPIC,
)

# N-D5: the `CONSUMER_GROUP` constant that used to live here has been removed.
# It was dead weight: nothing in Delta ever constructed a KafkaConsumer, so the
# group id was a declaration of an intent that no code backed. It also implied
# Delta owned an evidence subscription, which the run plan assigns to the
# Validation Engine (Pod Beta) -- a name that disagreed with the ownership
# model. A consumer group should be introduced together with the subscriber
# that uses it, in the pod that owns the subscription.
