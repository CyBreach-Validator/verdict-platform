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
    rule_name: str
    rule_type: str
    severity: str
    description: Optional[str] = None
    query: str
    status: str
    mitre_technique: Optional[str] = None

    class Config:
        from_attributes = True