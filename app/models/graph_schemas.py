from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class GraphDatasetCreate(BaseModel):
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "SocialNetwork"
            }
        }

class GraphDatasetResponse(BaseModel):
    id: str
    session_id: str
    name: str
    created_at: Any
    
    class Config:
        from_attributes = True

class NodeCreate(BaseModel):
    label: str
    properties: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "label": "Person",
                "properties": {
                    "name": "Alice",
                    "age": 30
                }
            }
        }

class EdgeCreate(BaseModel):
    from_node_id: int
    to_node_id: int
    type: str
    properties: Dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "from_node_id": 1,
                "to_node_id": 2,
                "type": "FOLLOWS",
                "properties": {
                    "since": "2024-01-01"
                }
            }
        }
