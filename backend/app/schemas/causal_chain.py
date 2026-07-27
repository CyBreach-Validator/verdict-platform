from pydantic import BaseModel


class RuleNode(BaseModel):
    id: int
    name: str
    technique: str | None = None


class ValidationNode(BaseModel):
    status: str


class ClassifierNode(BaseModel):
    status: str


class VerdictNode(BaseModel):
    id: int
    hash: str
    superseded: bool


class CausalChainResponse(BaseModel):
    rule: RuleNode
    event: dict
    validation: ValidationNode
    classifier: ClassifierNode
    verdict: VerdictNode