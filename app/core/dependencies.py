"""
Reusable FastAPI dependencies for authorization and validation.
"""
from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.graph import GraphDataset


async def get_valid_session(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Session:
    """
    Dependency to verify that the session exists and belongs to the current user.
    Automatically injected into route handlers.
    """
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def get_valid_tabular_dataset(
    session_id: str = Path(..., description="Session ID"),
    dataset_id: str = Path(..., description="Dataset ID"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> TabularDataset:
    """
    Dependency to verify that the tabular dataset exists and belongs to the user's session.
    Also validates session ownership.
    """
    # First verify session
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Then verify dataset
    result = await db.execute(
        select(TabularDataset).where(
            TabularDataset.id == dataset_id,
            TabularDataset.session_id == session_id
        )
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Tabular dataset not found")
    return dataset


async def get_valid_graph_dataset(
    session_id: str = Path(..., description="Session ID"),
    dataset_id: str = Path(..., description="Dataset ID"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> GraphDataset:
    """
    Dependency to verify that the graph dataset exists and belongs to the user's session.
    Also validates session ownership.
    """
    # First verify session
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Then verify dataset
    result = await db.execute(
        select(GraphDataset).where(
            GraphDataset.id == dataset_id,
            GraphDataset.session_id == session_id
        )
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Graph dataset not found")
    return dataset
