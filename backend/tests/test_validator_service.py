"""Tests for Delta's rule evaluation and the verdict vocabulary it produces.

Covers the M2 distinction that the revalidation path depends on:
  * `NoData`  - the rule could not be evaluated (evidence absent)
  * `Missed`  - the rule was evaluated and did not fire
  * `Detected`- the rule fired
"""

import json

import pytest

from app.contracts.verdict_event import (
    VERDICT_DETECTED,
    VERDICT_MISSED,
    VERDICT_NODATA,
)
from app.services.validator_service import (
    MalformedRuleQuery,
    validate_rule,
)

RULE = json.dumps(
    {
        "detection": {
            "selection": {
                "Image": "powershell",
                "CommandLine": "Invoke-Expression",
            }
        }
    }
)

FULL_EVENT = {
    "action_id": "act-1",
    "Image": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
    "CommandLine": "powershell -enc Invoke-Expression",
    "timestamp": "2026-09-28T10:00:00Z",
}


class TestMalformedQueries:
    def test_invalid_json_raises_client_error(self):
        with pytest.raises(MalformedRuleQuery):
            validate_rule("not json at all", {"action_id": "a"})

    def test_non_object_json_raises(self):
        with pytest.raises(MalformedRuleQuery):
            validate_rule("[1, 2, 3]", {"action_id": "a"})


class TestVerdictVocabulary:
    def test_full_match_is_detected(self):
        result = validate_rule(RULE, FULL_EVENT)
        assert result["status"] == VERDICT_DETECTED
        assert set(result["matched_fields"]) == {"Image", "CommandLine"}
        assert result["confidence"] == 1.0

    def test_present_but_different_value_is_missed(self):
        result = validate_rule(
            RULE, {**FULL_EVENT, "CommandLine": "powershell -enc Get-Process"}
        )
        assert result["status"] == VERDICT_MISSED
        assert result["confidence"] == 0.0

    def test_absent_field_is_nodata_not_missed(self):
        """A field the event does not carry means the rule is unevaluable."""

        event = {k: v for k, v in FULL_EVENT.items() if k != "CommandLine"}
        result = validate_rule(RULE, event)

        assert result["status"] == VERDICT_NODATA
        assert result["status"] != VERDICT_MISSED

    def test_nodata_is_never_spelled_with_a_space(self):
        event = {k: v for k, v in FULL_EVENT.items() if k != "CommandLine"}
        assert " " not in validate_rule(RULE, event)["status"]

    def test_rule_without_selection_is_nodata(self):
        result = validate_rule(json.dumps({"detection": {}}), FULL_EVENT)
        assert result["status"] == VERDICT_NODATA


class TestConfidenceScale:
    def test_confidence_is_always_within_unit_range(self):
        events = [
            FULL_EVENT,
            {**FULL_EVENT, "CommandLine": "cmd /c dir"},
            {k: v for k, v in FULL_EVENT.items() if k != "Image"},
            {},
        ]

        for event in events:
            confidence = validate_rule(RULE, event)["confidence"]
            assert 0.0 <= confidence <= 1.0, event


class TestContractFields:
    def test_result_carries_real_contract_values(self):
        result = validate_rule(RULE, FULL_EVENT)

        assert result["matched_evidence_ref"] == "act-1"
        assert result["mttd_seconds"] is not None
        assert result["mttd_seconds"] >= 0
        assert result["causal_chain"]
        assert all(isinstance(step, str) for step in result["causal_chain"])

    def test_mttd_is_none_without_a_timestamp(self):
        event = {k: v for k, v in FULL_EVENT.items() if k != "timestamp"}
        assert validate_rule(RULE, event)["mttd_seconds"] is None

    def test_causal_chain_never_leaks_raw_event_data(self):
        result = validate_rule(RULE, FULL_EVENT)
        assert "powershell -enc" not in " ".join(result["causal_chain"])
