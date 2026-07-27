from sqlalchemy import Column, Integer, String, Text

from app.database.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text)
    query = Column(Text, nullable=False)
    status = Column(String(20), default="Active")

    mitre_technique = Column(String(20), nullable=True)