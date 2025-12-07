from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class GraphDatasetCreate(BaseModel):
    name: str

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

class EdgeCreate(BaseModel):
    from_node_id: int
    to_node_id: int
    type: str
    properties: Dict[str, Any] = {}
