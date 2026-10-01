from typing import Optional

from pydantic import BaseModel


class RuleCreate(BaseModel):
    rule_name: str
    rule_type: str
    severity: str
    description: Optional[str] = None
    query: str
    status: str
    mitre_technique: Optional[str] = None


class RuleUpdate(BaseModel):
    rule_name: str
    rule_type: str
    severity: str
    description: Optional[str] = None
    query: str
    status: str
    mitre_technique: Optional[str] = None


class RuleResponse(BaseModel):
    id: int

    # `id` is the surrogate primary key and is not usable across pods. `rule_id`
    # is the canonical content hash that `verdict_events.rule_id` joins on, so a
    # caller had no way to learn the id its verdicts will be filed under: the
    # response omitted it entirely. Exposed here so a rule can be created and
    # then referenced by the exact id that validation resolves.
    rule_id: Optional[str] = None
    rule_name: str
    rule_type: str
    severity: str
    description: Optional[str] = None
    query: str
    status: str
    mitre_technique: Optional[str] = None

    class Config:
        from_attributes = True


class RuleComparisonProposed(BaseModel):
    """The candidate revision a caller wants diffed against the stored rule.

    N-D19: the compare endpoint used to return a hardcoded
    `"Suspicious PowerShell"` block in this shape, so the dashboard rendered a
    diff between a real rule and a fabricated one and the highlighting was
    meaningless. The proposal is now supplied by the caller; every field is
    optional so a partial revision compares only the fields it actually
    changes, and an omitted field falls back to the stored value.
    """

    title: Optional[str] = None
    query: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None