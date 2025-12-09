from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db, init_db
from app.core.dependencies import get_valid_session
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.schemas import SessionCreate, SessionResponse

router = APIRouter()

@router.on_event("startup")
async def on_startup():
    await init_db()

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED, summary="Create a new Session", description="Create a new isolated session for managing data.")
async def create_session(
    session_in: SessionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    new_session = Session(
        user_id=user_id,
        name=session_in.name,
        description=session_in.description
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    # Re-fetch with eager loading to satisfy Pydantic response model
    query = select(Session).options(selectinload(Session.tabular_datasets), selectinload(Session.graph_datasets)).where(Session.id == new_session.id)
    result = await db.execute(query)
    new_session = result.scalar_one()

    return new_session

@router.get("/", response_model=List[SessionResponse], summary="List all Sessions", description="Retrieve all sessions owned by the current user.")
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    query = select(Session).options(selectinload(Session.tabular_datasets), selectinload(Session.graph_datasets)).where(Session.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{session_id}", response_model=SessionResponse, summary="Get Session Details", description="Retrieve details of a specific session.")
async def get_session(
    session: Session = Depends(get_valid_session),
    db: AsyncSession = Depends(get_db)
):
    # Re-fetch with eager loading to satisfy Pydantic response model
    query = select(Session).options(
        selectinload(Session.tabular_datasets), 
        selectinload(Session.graph_datasets)
    ).where(Session.id == session.id)
    result = await db.execute(query)
    session_with_datasets = result.scalar_one()
    return session_with_datasets

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Session", description="Permanently delete a session and all its associated data.")
async def delete_session(
    session: Session = Depends(get_valid_session),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(session)
    await db.commit()
