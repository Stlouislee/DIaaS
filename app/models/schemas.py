from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Analysis 2024",
                "description": "Session for analyzing Q1 sales data"
            }
        }

class DatasetSummary(BaseModel):
    id: str
    name: str

class SessionResponse(SessionCreate):
    id: str
    user_id: str
    created_at: datetime
    tabular_datasets: List[DatasetSummary] = []
    graph_datasets: List[DatasetSummary] = []

    class Config:
        from_attributes = True
