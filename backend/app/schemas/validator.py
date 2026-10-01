from typing import Optional

from pydantic import BaseModel


class ValidationRequest(BaseModel):
    action_id: str
    rule_query: str
    event: dict

    # These make the `rule_id` this endpoint derives reproducible.
    #
    # `compute_rule_id` hashes rule_name + query + rule_type + mitre_technique
    # (app/utils/rule_hash_utils.py), and `create_rule` in
    # app/services/rule_service.py passes exactly those four when it stores a
    # rule. This endpoint used to compute
    # `compute_rule_id(rule_name=request.action_id, query=request.rule_query)` --
    # hashing the *action id* as though it were the rule name, and omitting
    # rule_type and mitre_technique entirely.
    #
    # Two consequences, both of which made the endpoint unusable:
    #   * The digest could never equal any stored rule's `rule_id`, because the
    #     name component was the wrong value and two components were missing.
    #   * `save_verdict` then inserted a `rule_id` with no matching row and
    #     PostgreSQL rejected it: ForeignKeyViolation on
    #     `verdict_events_rule_id_fkey`, surfaced as a bare HTTP 500.
    #
    # Optional so a caller sending only the original three fields still
    # validates; `rule_name` then falls back to `action_id`. Note that
    # `severity` is deliberately absent -- it is stored on the rule but is not
    # part of the hash, so accepting it here would imply it affects rule_id.
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    mitre_technique: Optional[str] = None