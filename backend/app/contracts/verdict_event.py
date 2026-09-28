"""
Single source of truth for the plan's Verdict Event v2.0 payload.

Plan Section 9 "Verdict Event (publish, v2.0)" requires exactly these fields:

    action_id, verdict, confidence, causal_chain, mttd_seconds,
    matched_evidence_ref, regulatory_control_refs, content_hash

Every Delta emit path (Kafka, WebSocket, REST response, DB row) previously
hand-built its own dict, so the three paths disagreed with each other and
with the frozen JSON Schema in `contracts/verdict-event/verdict.schema.json`.
This module owns:

  1. The canonical verdict token spelling (`NoData`, never `"No Data"`).
  2. `build_verdict_event(...)` -- the one serializer. It takes the real
     contract values, computes `content_hash` over the published payload
     itself, and returns a dict that validates against the frozen schema.
  3. `validate_verdict_event(...)` -- jsonschema validation against the
     frozen contract file, so a drift in a future field change fails loudly
     at publish time instead of silently.
"""

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

# Frozen contract lives at <repo>/contracts/verdict-event/verdict.schema.json
# This module lives at <repo>/backend/app/contracts/verdict_event.py
CONTRACT_DIR = Path(__file__).resolve().parents[3] / "contracts" / "verdict-event"
VERDICT_SCHEMA_PATH = CONTRACT_DIR / "verdict.schema.json"

# The one canonical verdict spelling (M2). Delta used to emit "No Data" on
# the re-validation and gap-closed paths; Alpha/Beta/Gamma use `NoData`.
VERDICT_DETECTED = "Detected"
VERDICT_MISSED = "Missed"
VERDICT_PARTIAL = "Partial"
VERDICT_NODATA = "NoData"

CANONICAL_VERDICTS = (
    VERDICT_DETECTED,
    VERDICT_MISSED,
    VERDICT_PARTIAL,
    VERDICT_NODATA,
)

# Legacy spellings still present in stored rows; normalised on read so a
# pre-migration row can never leak the old token back onto the wire.
_VERDICT_ALIASES = {
    "No Data": VERDICT_NODATA,
    "no data": VERDICT_NODATA,
    "NODATA": VERDICT_NODATA,
    "detected": VERDICT_DETECTED,
    "DETECTED": VERDICT_DETECTED,
    "missed": VERDICT_MISSED,
    "MISSED": VERDICT_MISSED,
    "partial": VERDICT_PARTIAL,
    "PARTIAL": VERDICT_PARTIAL,
}

# Fallback content hash input when a caller supplies no evidence ref, so the
# digest is always reproducible from the published payload.
UNKNOWN_EVIDENCE_REF = "unknown-evidence"


class VerdictContractError(ValueError):
    """Raised when a payload cannot be built or violates the frozen schema."""


def normalize_verdict(verdict: str) -> str:
    """Map any known legacy spelling onto the canonical v2.0 token."""

    if verdict in CANONICAL_VERDICTS:
        return verdict

    return _VERDICT_ALIASES.get(verdict, verdict)


def normalize_confidence(confidence: Any) -> float:
    """Clamp confidence into the plan's 0.0-1.0 range.

    Delta's REST/DB paths historically stored `95` on a 0-100 scale while the
    Kafka path divided by 100. Anything above 1.0 is treated as a percentage;
    everything else is clamped.
    """

    value = float(confidence)

    if value > 1.0:
        value = value / 100.0

    return round(min(max(value, 0.0), 1.0), 4)


@lru_cache(maxsize=1)
def _verdict_schema() -> Dict[str, Any]:
    with open(VERDICT_SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _verdict_validator():
    return jsonschema.Draft202012Validator(_verdict_schema())


def validate_verdict_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a payload against the frozen v2.0 JSON Schema.

    Raises `VerdictContractError` listing every violation, so a future field
    change fails at publish time rather than drifting silently.
    """

    errors = sorted(
        _verdict_validator().iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )

    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise VerdictContractError(
            f"Verdict event does not satisfy the frozen v2.0 contract: {details}"
        )

    return payload


def compute_content_hash(payload: Dict[str, Any]) -> str:
    """SHA-256 over the published v2.0 payload itself.

    The digest covers every contract field except `content_hash` itself, so any
    consumer holding the event can re-derive and verify it. Canonical
    serialisation (sorted keys, no insignificant whitespace) keeps the digest
    stable across processes.
    """

    hashable = {k: v for k, v in payload.items() if k != "content_hash"}

    serialized = json.dumps(
        hashable,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()


def build_verdict_event(
    action_id: Any,
    verdict: str,
    confidence: Any,
    causal_chain: Optional[List[str]] = None,
    mttd_seconds: Optional[float] = None,
    matched_evidence_ref: Optional[str] = None,
    regulatory_control_refs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the one canonical v2.0 verdict payload.

    The returned dict satisfies the frozen schema (all 8 required fields, no
    extras) and carries a `content_hash` computed over itself.
    """

    if not action_id:
        raise VerdictContractError("action_id is required for a v2.0 verdict event")

    canonical_verdict = normalize_verdict(verdict)

    if canonical_verdict not in CANONICAL_VERDICTS:
        raise VerdictContractError(
            f"verdict must be one of {CANONICAL_VERDICTS}, got {verdict!r}"
        )

    payload: Dict[str, Any] = {
        "action_id": str(action_id),
        "verdict": canonical_verdict,
        "confidence": normalize_confidence(confidence),
        "causal_chain": [str(step) for step in (causal_chain or [])],
        "mttd_seconds": None if mttd_seconds is None else float(mttd_seconds),
        "matched_evidence_ref": (
            str(matched_evidence_ref)
            if matched_evidence_ref is not None
            else UNKNOWN_EVIDENCE_REF
        ),
        "regulatory_control_refs": [
            str(ref) for ref in (regulatory_control_refs or [])
        ],
    }

    payload["content_hash"] = compute_content_hash(payload)

    return validate_verdict_event(payload)


def verify_content_hash(payload: Dict[str, Any]) -> bool:
    """Re-derive the digest of a received event and compare it."""

    if "content_hash" not in payload:
        return False

    return compute_content_hash(payload) == payload["content_hash"]
