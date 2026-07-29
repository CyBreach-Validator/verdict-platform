from datetime import datetime
from pydantic import BaseModel


class ConnectorResponse(BaseModel):
    id: int
    name: str
    status: str
    version: str | None = None
    last_seen: datetime | None = None

    class Config:
        from_attributes = True