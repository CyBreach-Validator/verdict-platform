"""
Plan Section 5 "Message Bus Topics" -- the one shared topic manifest.

Every producer and consumer in Pod Delta resolves topic names from here so
there is a single bus contract. The broker is injected via `KAFKA_BOOTSTRAP_SERVERS`
(defaulting to the local hybrid-run broker on 9092) rather than hardcoded in
each module.
"""

import os
from pathlib import Path

import yaml

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# --- Plan Section 5 topics -------------------------------------------------

EVIDENCE_TOPIC = "cybreach.evidence.v1"
VERDICT_TOPIC = "cybreach.verdicts.v2"
GAP_CLOSED_TOPIC = "cybreach.gap_closed.v2"
REVALIDATION_TOPIC = "cybreach.revalidation.v1"
CONNECTOR_HEALTH_TOPIC = "cybreach.connector.health.v1"


def _load_shared_topics() -> dict:
    """Resolve the topic names from the single workspace manifest when present.

    M5/B1: the five names below used to be one of three hand-written copies that
    only agreed by discipline. The authoritative list now lives in the
    integration environment's `topics.yaml`; point `M2_TOPICS_PATH` at it (the
    root `docker-compose.yml` run sets it) and Delta reads the names from the
    one shared file instead of its private copy. If the file is absent (a
    standalone Delta checkout, or a pod-local test run) the constants above
    remain the fallback, so nothing breaks -- but the constants are asserted
    against the shared manifest by the workspace contract test.
    """

    manifest = os.getenv("M2_TOPICS_PATH")
    if not manifest:
        return {}

    path = Path(manifest)
    if not path.is_file():
        return {}

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}

    topics = data.get("topics") if isinstance(data, dict) else None
    if not isinstance(topics, list):
        return {}

    return {
        entry["name"]: entry
        for entry in topics
        if isinstance(entry, dict) and "name" in entry
    }


_TOPICS = _load_shared_topics()

if _TOPICS:
    EVIDENCE_TOPIC = _TOPICS.get("cybreach.evidence.v1", {}).get("name", EVIDENCE_TOPIC)
    VERDICT_TOPIC = _TOPICS.get("cybreach.verdicts.v2", {}).get("name", VERDICT_TOPIC)
    GAP_CLOSED_TOPIC = _TOPICS.get("cybreach.gap_closed.v2", {}).get("name", GAP_CLOSED_TOPIC)
    REVALIDATION_TOPIC = _TOPICS.get("cybreach.revalidation.v1", {}).get("name", REVALIDATION_TOPIC)
    CONNECTOR_HEALTH_TOPIC = _TOPICS.get("cybreach.connector.health.v1", {}).get("name", CONNECTOR_HEALTH_TOPIC)

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
