from pydantic import BaseModel


class ValidationRequest(BaseModel):
    action_id: str
    rule_query: str
    event: dict