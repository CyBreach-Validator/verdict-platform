from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class Connector(Base):
    # N-D12: this used to be named `connectors`, which collides with the table
    # Pod Gamma creates and with the canonical Connector Framework registry that
    # plan Section 7 assigns to Pod Alpha. Delta stores only health metadata for
    # its own dashboard, so it gets its own namespace. `tests/
    # test_schema_parity.py::test_no_connector_table_name_collision` fails the
    # build if the name ever comes back.
    __tablename__ = "platform_connector_health"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    status = Column(String, nullable=False)

    version = Column(String, nullable=True)

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )
