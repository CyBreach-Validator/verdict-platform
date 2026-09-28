from datetime import datetime

from pydantic import BaseModel


class VerdictResponse(BaseModel):
    id: int
    action_id: str
    # B6: string, matching the canonical content-hash rule identifier and the
    # column type. Declaring it as `int` here made FastAPI reject every real
    # response with a 500 validation error, and it is the type the frontend is
    # migrated to.
    rule_id: str
    rule_name: str
    verdict: str
    # B5: 0.0-1.0.
    confidence: float
    causal_chain: list[str]
    mttd_seconds: float | None = None
    matched_evidence_ref: str | None = None
    regulatory_control_refs: list[str]
    event_data: str
    # M12: the contract calls this `content_hash`; the old `verdict_hash` name
    # did not match the wire format and the column no longer exists.
    content_hash: str
    is_superseded: bool
    superseded_by: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True
