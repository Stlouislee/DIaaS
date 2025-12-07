from sqlalchemy import Column, String, ForeignKey, DateTime
from app.core.database import Base
from datetime import datetime
import uuid

class TabularDataset(Base):
    __tablename__ = "tabular_datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    # The physical table name in Postgres will be derived, e.g., "dataset_{id}"
    # We store the user-facing name here.
    created_at = Column(DateTime, default=datetime.utcnow)
