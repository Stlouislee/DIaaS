from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class TabularDatasetCreate(BaseModel):
    name: str # Dataset name
    schema_def: Dict[str, str] = Field(..., description="Map of 'column_name': 'SQL_TYPE'")

class TabularDatasetResponse(BaseModel):
    id: str
    session_id: str
    name: str
    created_at: Any

    class Config:
        from_attributes = True

class RowInsert(BaseModel):
    rows: List[Dict[str, Any]]

class RecordResponse(BaseModel):
    data: List[Dict[str, Any]]
    count: int
