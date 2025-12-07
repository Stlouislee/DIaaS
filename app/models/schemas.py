from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class SessionResponse(SessionCreate):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
