
from fastapi import FastAPI, APIRouter

from app.core.config import settings
from app.api.routes import users, sessions, tabular, graph, export, query
from app.core.neo4j_db import init_neo4j, close_neo4j

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(tabular.router, prefix="/sessions", tags=["tabular"])
api_router.include_router(graph.router, prefix="/sessions", tags=["graph"])
api_router.include_router(export.router, prefix="/sessions", tags=["export"])
api_router.include_router(query.router, prefix="/sessions", tags=["query"])

@app.on_event("startup")
async def startup_event():
    await init_neo4j()

@app.on_event("shutdown")
async def shutdown_event():
    await close_neo4j()

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}
