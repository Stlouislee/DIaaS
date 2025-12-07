import re
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")

async def get_current_user_id(api_key: str = Security(api_key_header)) -> str:
    """
    Validates API Key and returns it as the user ID.
    If ALLOWED_KEYS is configured, checks against the list.
    Otherwise, just validates format.
    """
    # 1. Format Validation
    if not KEY_PATTERN.match(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key format. Must be 8-64 alphanumeric characters (including - and _)."
        )

    # 2. Permission Check (if configured)
    if settings.ALLOWED_KEYS and api_key not in settings.ALLOWED_KEYS:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized."
        )
    
    return api_key
