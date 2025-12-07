from sqlalchemy import Column, String, ForeignKey, DateTime
from app.core.database import Base
from datetime import datetime
import uuid

class GraphDataset(Base):
    __tablename__ = "graph_datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    # Neo4j uses Labels to distinguish datasets.
    # Logic: Label = "Graph_" + ID (sanitized)
    created_at = Column(DateTime, default=datetime.utcnow)
