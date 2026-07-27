from datetime import datetime

from pydantic import BaseModel


class VerdictResponse(BaseModel):
    id: int
    rule_id: int
    rule_name: str
    verdict: str
    event_data: str
    verdict_hash: str
    is_superseded: bool
    superseded_by: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True