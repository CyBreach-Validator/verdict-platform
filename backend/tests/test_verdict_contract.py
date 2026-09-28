"""Tests for the frozen Verdict Event v2.0 contract (plan Section 9).

These lock in the M1-M4 fixes:
  * exactly the 8 contract fields, no extras
  * `NoData`, never `"No Data"`
  * confidence always 0.0-1.0
  * `content_hash` is reproducible by any consumer
"""

import pytest

from app.contracts.verdict_event import (
    CANONICAL_VERDICTS,
    VerdictContractError,
    build_verdict_event,
    compute_content_hash,
    normalize_confidence,
    normalize_verdict,
    validate_verdict_event,
    verify_content_hash,
)

REQUIRED_FIELDS = {
    "action_id",
    "verdict",
    "confidence",
    "causal_chain",
    "mttd_seconds",
    "matched_evidence_ref",
    "regulatory_control_refs",
    "content_hash",
}


def _event(**overrides):
    kwargs = {
        "action_id": "act-1",
        "verdict": "Detected",
        "confidence": 0.9,
        "causal_chain": ["step-a", "step-b"],
        "mttd_seconds": 12.5,
        "matched_evidence_ref": "ev-1",
        "regulatory_control_refs": ["ISO27001-A.5.15"],
    }
    kwargs.update(overrides)
    return build_verdict_event(**kwargs)


class TestRequiredFields:
    def test_payload_has_exactly_the_contract_fields(self):
        assert set(_event()) == REQUIRED_FIELDS

    @pytest.mark.parametrize("verdict", CANONICAL_VERDICTS)
    def test_every_canonical_verdict_validates(self, verdict):
        assert validate_verdict_event(_event(verdict=verdict))

    def test_action_id_is_required(self):
        with pytest.raises(VerdictContractError):
            _event(action_id="")

    def test_unknown_verdict_is_rejected(self):
        with pytest.raises(VerdictContractError):
            _event(verdict="Probably Fine")


class TestVerdictSpelling:
    @pytest.mark.parametrize(
        "legacy,canonical",
        [
            ("No Data", "NoData"),
            ("no data", "NoData"),
            ("NODATA", "NoData"),
            ("detected", "Detected"),
            ("MISSED", "Missed"),
        ],
    )
    def test_legacy_spellings_normalise(self, legacy, canonical):
        assert normalize_verdict(legacy) == canonical
        assert _event(verdict=legacy)["verdict"] == canonical

    def test_nodata_is_never_spelled_with_a_space(self, monkeypatch):
        monkeypatch.setattr(
            "app.contracts.verdict_event.UNKNOWN_EVIDENCE_REF", "unknown-evidence"
        )
        assert " " not in _event(verdict="No Data")["verdict"]


class TestConfidence:
    @pytest.mark.parametrize(
        "given,expected",
        [
            (0.93, 0.93),
            (93, 0.93),        # legacy 0-100 scale
            (100, 1.0),
            (0, 0.0),
            (-5, 0.0),         # clamped
            (140, 1.0),        # clamped
        ],
    )
    def test_confidence_always_lands_in_unit_range(self, given, expected):
        assert normalize_confidence(given) == expected
        assert 0.0 <= _event(confidence=given)["confidence"] <= 1.0


class TestContentHash:
    def test_hash_is_self_verifying(self):
        event = _event()
        assert verify_content_hash(event) is True

    def test_hash_is_stable_across_key_order(self):
        forward = _event()
        reversed_event = dict(reversed(list(forward.items())))
        assert compute_content_hash(forward) == compute_content_hash(reversed_event)

    def test_tampering_is_detected(self):
        event = _event()
        event["verdict"] = "Missed"
        assert verify_content_hash(event) is False

    def test_hash_excludes_itself(self):
        event = _event()
        without_hash = {k: v for k, v in event.items() if k != "content_hash"}
        assert compute_content_hash(event) == compute_content_hash(without_hash)

    def test_hash_covers_every_other_contract_field(self):
        baseline = _event()

        for field in REQUIRED_FIELDS - {"content_hash"}:
            tampered = dict(baseline)
            original = tampered[field]
            tampered[field] = [] if isinstance(original, list) else "changed"
            assert verify_content_hash(tampered) is False, (
                f"content_hash does not cover {field}"
            )


class TestOptionalFields:
    def test_missing_evidence_ref_still_produces_a_valid_event(self):
        event = _event(matched_evidence_ref=None)
        assert event["matched_evidence_ref"]
        assert verify_content_hash(event) is True

    def test_absent_collections_default_to_empty_lists(self):
        event = build_verdict_event(
            action_id="act-1", verdict="Detected", confidence=0.5
        )
        assert event["causal_chain"] == []
        assert event["regulatory_control_refs"] == []
        assert event["mttd_seconds"] is None
