from sqlalchemy import JSON, Column, Integer, String, Text

from app.database.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)

    # B6: the canonical content-hash rule identifier shared across pods, keyed
    # to the string `rule_id` Pod Alpha owns. `id` stays as Delta's local
    # surrogate key for its own routes.
    rule_id = Column(String(64), nullable=True, index=True, unique=True)

    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text)
    query = Column(Text, nullable=False)
    status = Column(String(20), default="Pending")

    mitre_technique = Column(String(20), nullable=True)

    # One of the v2.0 contract fields. It travels with the verdict rather than
    # being invented at publish time (N-D10), so a rule carries its own
    # regulatory provenance and the serializer just reads it.
    regulatory_control_refs = Column(JSON, nullable=False, default=list)
