from fastapi import APIRouter
from app.api.routes import users, sessions, tabular

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(tabular.router, prefix="/sessions", tags=["tabular"]) # Mounted under sessions


