from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import secrets
import uuid

router = APIRouter()

class UserResponse(BaseModel):
    user_id: str
    api_key: str
    message: str

@router.post("/register", response_model=UserResponse)
def register_user():
    """
    Generates a new random API Key.
    In a real system, we might save this to a DB.
    Here, we generate a valid key that the user can use immediately 
    (assuming ALLOWED_KEYS is empty or they add it manually).
    """
    # Generate a secure random key
    new_key = secrets.token_urlsafe(32)
    return {
        "user_id": new_key, # In this design, key is ID
        "api_key": new_key,
        "message": "Start using this key in X-API-Key header."
    }
