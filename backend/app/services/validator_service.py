"""Sigma rule evaluation and the verdict vocabulary it produces.

M2 is the distinction the whole revalidation flow turns on:

    NoData   - the rule could not be evaluated (a field the rule needs is absent)
    Missed   - the rule was evaluated and did not fire
    Detected - the rule fired

The old implementation returned `Missed` whenever a selected field was missing
from the event, which conflated "the evidence is not there" with "the evidence
is there and the rule did not match". `POST /verdicts/{id}/revalidate` credits a
refund on `UNCHANGED`, so that conflation made a gap look like a clean miss.

N-D10 also applies here: the returned dict carries real v2.0 contract values
(`mttd_seconds`, `causal_chain`, `matched_evidence_ref`) instead of the
hardcoded `None`/`[]`/action-id-as-evidence-ref placeholders the emit paths used
to invent.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.contracts.verdict_event import (
    VERDICT_DETECTED,
    VERDICT_MISSED,
    VERDICT_NODATA,
)


class MalformedRuleQuery(ValueError):
    """A rule query that cannot be evaluated at all.

    Distinct from `NoData` (the rule is fine, the evidence is not) and from
    `Missed` (both are fine, it just did not match). The API layer turns this
    into a 422 -- a client sent something unusable -- rather than a 500.
    """


def _mttd_seconds(event: dict) -> float | None:
    """Seconds between the evidence event and the moment it was evaluated.

    `None` when the event carries no usable timestamp: inventing a number here
    is exactly the N-D10 hollowing-out the v2.0 contract was written to stop.
    """

    raw = event.get("timestamp")

    if not raw:
        return None

    if isinstance(raw, (int, float)):
        occurred = datetime.fromtimestamp(float(raw), tz=timezone.utc)
    else:
        text = str(raw).strip().replace("Z", "+00:00")

        try:
            occurred = datetime.fromisoformat(text)
        except ValueError:
            return None

        if occurred.tzinfo is None:
            occurred = occurred.replace(tzinfo=timezone.utc)

    elapsed = (datetime.now(tz=timezone.utc) - occurred).total_seconds()

    # A clock skew or a future-dated event must not produce a negative MTTD.
    return max(elapsed, 0.0)


def _field_matches(expected: Any, actual: str) -> bool:
    """Case-insensitive substring match, tolerating Sigma's `*` wildcard.

    A list under one key is a Sigma OR-set, so any member matching is enough.
    """

    if isinstance(expected, list):
        return any(
            _field_matches(member, actual) for member in expected
        )

    needle = str(expected).replace("*", "").strip().lower()

    if not needle:
        return False

    return needle in actual.lower()


def _selection_of(detection: dict) -> Dict[str, Any]:
    """Accept both `{"detection": {"selection": ...}}` and a bare `selection`."""

    if "detection" in detection:
        return detection.get("detection", {}).get("selection", {}) or {}

    return detection.get("selection", {}) or {}


def _matched_evidence_ref(event: dict) -> str | None:
    """N-D10: the reference to the evidence this verdict rests on.

    The previous implementation returned `event["action_id"]`, i.e. the
    contract field made the evidence point at *itself*. `matched_evidence_ref`
    is supposed to identify the underlying evidence artifact, so it is resolved
    from the event's own identity fields, preferring the most specific one
    available.

    `ValidationRequest` carries only `action_id`, `rule_query` and `event`, so
    the evidence identity has to come from the event body; when an event truly
    carries no identifier beyond its action id, the action id is the honest
    answer and is returned last rather than fabricated away.
    """

    for key in (
        "evidence_id",
        "event_id",
        "alert_id",
        "finding_id",
        "record_id",
        "uuid",
    ):
        value = event.get(key)
        if value not in (None, ""):
            return str(value)

    # A nested identity, as SIEM exports commonly carry it.
    for container in ("event", "data", "raw"):
        nested = event.get(container)
        if isinstance(nested, dict):
            for key in ("evidence_id", "event_id", "id", "uuid"):
                value = nested.get(key)
                if value not in (None, ""):
                    return str(value)

    return event.get("action_id")


def validate_rule(rule_query: str, event: dict) -> dict:
    """Evaluate one Sigma-style rule against one evidence event."""

    try:
        parsed = json.loads(rule_query)
    except (json.JSONDecodeError, TypeError) as exc:
        raise MalformedRuleQuery(
            f"rule query is not valid JSON: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise MalformedRuleQuery(
            "rule query must be a JSON object, got "
            f"{type(parsed).__name__}"
        )

    selection = _selection_of(parsed)

    if not selection:
        # Nothing to evaluate. This is NoData, not Missed: the rule is missing a
        # selection rather than the evidence failing to match one.
        return {
            "status": VERDICT_NODATA,
            "confidence": 0.0,
            "matched_fields": [],
            "matched_evidence_ref": _matched_evidence_ref(event),
            "mttd_seconds": _mttd_seconds(event),
            "causal_chain": [
                "The rule declares no selection, so there is nothing to "
                "evaluate against the event.",
                "Emitting NoData rather than Missed: the rule is unusable, "
                "not unsatisfied.",
            ],
            "message": "Rule has no detection selection.",
        }

    evaluated: List[str] = []

    for field, expected in selection.items():
        actual = event.get(field)

        if actual is None:
            return {
                "status": VERDICT_NODATA,
                "confidence": 0.0,
                "matched_fields": evaluated,
                "matched_evidence_ref": _matched_evidence_ref(event),
                "mttd_seconds": _mttd_seconds(event),
                "causal_chain": [
                    f"Field '{field}' is required by the rule but absent from "
                    "the event.",
                    "The rule cannot be evaluated, so NoData is emitted; "
                    "reporting Missed here would claim the evidence was "
                    "examined and rejected when it was never present.",
                ],
                "message": f"Field '{field}' is missing from the event.",
            }

        if not _field_matches(expected, str(actual)):
            return {
                "status": VERDICT_MISSED,
                "confidence": 0.0,
                "matched_fields": evaluated,
                "matched_evidence_ref": _matched_evidence_ref(event),
                "mttd_seconds": _mttd_seconds(event),
                "causal_chain": [
                    f"Evaluated {len(selection)} selected field(s); "
                    f"{len(evaluated)} matched before the failure.",
                    f"Field '{field}' is present in the event but its value "
                    "does not satisfy the rule's condition.",
                    "The rule was evaluable and did not fire, so Missed is "
                    "emitted.",
                ],
                "message": f"Field '{field}' did not match.",
            }

        evaluated.append(field)

    return {
        "status": VERDICT_DETECTED,
        "confidence": 1.0,
        "matched_fields": evaluated,
        "matched_evidence_ref": _matched_evidence_ref(event),
        "mttd_seconds": _mttd_seconds(event),
        "causal_chain": [
            f"Evaluated all {len(selection)} selected field(s) from the rule.",
            "Every selected field satisfied its condition, so the rule fired.",
            "Emitting Detected.",
        ],
        "message": "All required fields matched.",
    }
