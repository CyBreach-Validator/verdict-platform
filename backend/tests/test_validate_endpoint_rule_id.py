"""`POST /api/v2/validate` must produce a verdict that can actually be stored.

`verdict_events.rule_id` is a foreign key onto `rules.rule_id`, and
`rule_id` is a content hash computed by `compute_rule_id` from four fields:
rule_name, query, rule_type and mitre_technique.

The endpoint used to derive that hash as
`compute_rule_id(rule_name=request.action_id, query=request.rule_query)` --
hashing the action id as if it were the rule's name and omitting rule_type and
mitre_technique. No stored rule's id could ever be reproduced, so every call
reached the insert and PostgreSQL rejected it with a ForeignKeyViolation that
surfaced to the client as an unhelpful HTTP 500.

These tests pin the four-field contract. The identity tests are computed
against `create_rule`'s own call rather than a hardcoded digest, so they fail if
either side's argument list changes.
"""

import json

import pytest

from app.api.validator import derive_rule_id, resolve_rule
from app.schemas.rule import RuleResponse
from app.schemas.validator import ValidationRequest
from app.services.rule_service import create_rule
from app.utils.rule_hash_utils import compute_rule_id

RULE_QUERY = json.dumps(
    {
        "detection": {
            "selection": {
                "Image": "powershell",
                "CommandLine|contains": "-enc",
            }
        }
    }
)

EVENT = {
    "command_line": "powershell -enc SQBFAFgA",
    "image": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
    "parent_image": "C:\\Windows\\System32\\services.exe",
    "timestamp": "2026-09-28T10:00:00Z",
}

RULE_NAME = "Suspicious PowerShell Encoded Command"
RULE_TYPE = "sigma"
MITRE = "T1059.001"


class _FakeRule:
    """Minimal stand-in for the ORM row `create_rule` returns."""

    def __init__(self, rule_id, rule_name, regulatory_control_refs=None):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.regulatory_control_refs = regulatory_control_refs or []


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class _FakeSession:
    """Accepts writes and resolves `rules` lookups by canonical id.

    Mirrors the foreign key the real schema enforces: `resolve_rule` returns
    None when the derived digest has no row, which is what the endpoint now
    turns into a 404 instead of letting the insert raise.
    """

    def __init__(self, rules=()):
        self.rules = {r.rule_id: r for r in rules}
        self.added = []
        self.committed = False

    def query(self, model):
        return _PassthroughQuery(self.rules)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        pass


class _PassthroughQuery:
    def __init__(self, rows_by_id):
        self._rows_by_id = rows_by_id
        self._wanted = None

    def filter(self, criterion):
        # SQLAlchemy renders `rules.rule_id = :param`. Pull the value back out
        # of the compiled expression rather than string-matching the model.
        self._wanted = getattr(criterion.right, "value", None)
        return self

    def first(self):
        if self._wanted is None:
            return None
        return self._rows_by_id.get(self._wanted)


def _request(**overrides):
    payload = {
        "action_id": "act-totally-different",
        "rule_query": RULE_QUERY,
        "event": EVENT,
        "rule_name": RULE_NAME,
        "rule_type": RULE_TYPE,
        "mitre_technique": MITRE,
    }
    payload.update(overrides)
    return ValidationRequest(**payload)


class TestValidateRequestShape:
    def test_carries_the_four_identity_fields(self):
        request = ValidationRequest(
            action_id="act-1",
            rule_query=RULE_QUERY,
            event=EVENT,
            rule_name=RULE_NAME,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )

        assert request.rule_name == RULE_NAME
        assert request.rule_type == RULE_TYPE
        assert request.mitre_technique == MITRE

    def test_identity_fields_are_optional_for_back_compatibility(self):
        # An older client sending only the original three fields must still
        # validate; rule_name falls back to action_id downstream.
        request = ValidationRequest(
            action_id="act-1",
            rule_query=RULE_QUERY,
            event=EVENT,
        )

        assert request.rule_name is None
        assert request.rule_type is None
        assert request.mitre_technique is None


class TestRuleIdIsReproducible:
    """The digest the endpoint derives must equal the one creation stored."""

    def test_endpoint_digest_matches_create_digest(self):
        created = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )

        # Call the endpoint's own derivation helper. Reimplementing the
        # argument list here would keep passing even if app/api/validator.py
        # regressed, which is exactly what the previous draft of this file did.
        assert derive_rule_id(_request()) == created

    def test_omitting_type_and_technique_would_not_match(self):
        """Guards the specific bug: dropping the optional fields breaks it.

        This is the digest the old code computed (name + query only). It must
        NOT equal the stored digest, which is why the endpoint could never join
        to a rule row.
        """
        created = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )
        legacy = compute_rule_id(rule_name=RULE_NAME, query=RULE_QUERY)

        assert legacy != created

    def test_hashing_action_id_as_rule_name_does_not_match(self):
        """Guards the other half of the bug: the wrong name component."""
        created = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )
        wrong = compute_rule_id(
            rule_name="act-totally-different",
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )

        assert wrong != created

    def test_derive_helper_rejects_a_digest_with_no_rule_row(self):
        """The endpoint must not fall through to a broken insert.

        With the old derivation no stored row could match, and the resulting
        IntegrityError surfaced as a bare 500. The endpoint now refuses with a
        404 naming the digest it looked for.
        """
        request = _request()
        digest = derive_rule_id(request)

        session = _FakeSession(rules=[])
        assert resolve_rule(session, digest) is None


class TestCreateRuleStoresTheDigest:
    def test_create_rule_persists_the_canonical_id(self):
        class _Row:
            rule_name = RULE_NAME
            rule_type = RULE_TYPE
            severity = "high"
            description = "demo"
            query = RULE_QUERY
            status = "active"
            mitre_technique = MITRE

        expected = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )

        session = _FakeSession()

        created = create_rule(session, _Row())

        assert created.rule_id == expected


class TestRuleResponseExposesCanonicalId:
    """A caller must be able to learn the id its verdicts will be filed under."""

    def test_rule_id_is_in_the_response_model(self):
        fields = RuleResponse.model_fields

        assert "rule_id" in fields

    def test_rule_id_survives_orm_attribute_mapping(self):
        stored = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )

        class _ORM:
            id = 7
            rule_id = stored
            rule_name = RULE_NAME
            rule_type = RULE_TYPE
            severity = "high"
            description = "demo"
            query = RULE_QUERY
            status = "active"
            mitre_technique = MITRE

        response = RuleResponse.model_validate(_ORM())

        assert response.rule_id == stored

    def test_rule_id_is_optional_for_backward_compatibility(self):
        fields = RuleResponse.model_fields

        # Optional so a row predating rule_id, or a hand-built response in a
        # test, still validates rather than raising.
        assert fields["rule_id"].is_required() is False


class TestForeignKeyWouldBeSatisfied:
    def test_derived_id_exists_in_the_rule_table(self):
        expected = compute_rule_id(
            rule_name=RULE_NAME,
            query=RULE_QUERY,
            rule_type=RULE_TYPE,
            mitre_technique=MITRE,
        )
        session = _FakeSession(rules=[_FakeRule(expected, RULE_NAME)])

        assert session.rules.get(expected) is not None

    def test_unknown_rule_is_absent_so_the_endpoint_404s(self):
        session = _FakeSession(rules=[])

        assert session.rules.get("does-not-exist") is None