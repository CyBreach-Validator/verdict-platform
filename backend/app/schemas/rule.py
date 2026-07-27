from pydantic import BaseModel


class RuleCreate(BaseModel):
    rule_name: str
    rule_type: str
    severity: str
    description: str
    query: str
    status: str
    mitre_technique: str



class RuleUpdate(BaseModel):
    rule_name: str
    rule_type: str
    severity: str
    description: str
    query: str
    status: str
    mitre_technique: str



class RuleResponse(BaseModel):
    id: int
    rule_name: str
    rule_type: str
    severity: str
    description: str
    query: str
    status: str
    mitre_technique: str


    class Config:
        from_attributes = True