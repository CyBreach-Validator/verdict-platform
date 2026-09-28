"""
Canonical rule content hashing (plan Section 9).

A detection rule's identity across pods is the SHA-256 digest of its content,
not a per-pod integer sequence. Pod Alpha assigns `rule_id` when it ingests a
rule; Delta computes the same digest for any rule it creates locally, so an
Alpha-ingested rule and a Delta-created one with identical content resolve to
the same id and verdicts stay joinable across pods.
"""

import hashlib
import json
from typing import Any, Dict, Optional


def compute_rule_id(
    rule_name: str,
    query: Any,
    rule_type: Optional[str] = None,
    mitre_technique: Optional[str] = None,
) -> str:
    """
    Return the canonical 64-hex content hash used as `rule_id`.
    """

    payload: Dict[str, Any] = {
        "rule_name": rule_name,
        "query": _canonical_query(query),
        "rule_type": rule_type,
        "mitre_technique": mitre_technique,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()


def _canonical_query(query: Any) -> Any:
    """
    Normalise a rule body so semantically identical rules hash identically
    regardless of key order or whether the body arrived as JSON text.
    """

    if isinstance(query, str):
        try:
            query = json.loads(query)
        except (TypeError, json.JSONDecodeError):
            return query.strip()

    return query
