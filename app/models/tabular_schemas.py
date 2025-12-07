from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class TabularDatasetCreate(BaseModel):
    name: str # Dataset name
    schema_def: Dict[str, str] = Field(..., description="Map of 'column_name': 'SQL_TYPE'")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "User_Metrics",
                "schema_def": {
                    "username": "VARCHAR",
                    "login_count": "INTEGER",
                    "last_active": "TIMESTAMP"
                }
            }
        }

class TabularDatasetResponse(BaseModel):
    id: str
    session_id: str
    name: str
    created_at: Any

    class Config:
        from_attributes = True

class RowInsert(BaseModel):
    rows: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "rows": [
                    {"username": "alice", "login_count": 5, "last_active": "2024-01-01T10:00:00"},
                    {"username": "bob", "login_count": 2, "last_active": "2024-01-02T11:00:00"}
                ]
            }
        }

class RecordResponse(BaseModel):
    data: List[Dict[str, Any]]
    count: int
