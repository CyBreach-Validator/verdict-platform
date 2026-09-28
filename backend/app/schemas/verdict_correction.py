from pydantic import BaseModel


class VerdictCorrectionRequest(BaseModel):
    verdict: str
    # Optional overrides for the two contract values a correction may legitimately
    # change. Left unset, `correct_verdict` carries the original values forward.
    confidence: float | None = None
    causal_chain: list[str] | None = None


class VerdictCorrectionResponse(BaseModel):
    id: int
    action_id: str
    # B6: string, as in the column and the wire contract.
    rule_id: str
    rule_name: str
    verdict: str
    confidence: float
    causal_chain: list[str]
    # M12: `content_hash` is the contract field name.
    content_hash: str
