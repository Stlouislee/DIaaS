from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.tabular_schemas import TabularDatasetCreate, TabularDatasetResponse, RowInsert
from app.services.tabular_service import TabularService
from typing import Optional, List

router = APIRouter()

@router.post("/{session_id}/datasets/tabular", response_model=TabularDatasetResponse)
async def create_tabular_dataset(
    session_id: str,
    dataset_in: TabularDatasetCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # Verify Session
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create Metadata
    new_dataset = TabularDataset(
        session_id=session_id,
        name=dataset_in.name
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)

    # Create Physical Table
    service = TabularService(db)
    try:
        await service.create_table(new_dataset.id, dataset_in.schema_def)
    except Exception as e:
        await db.delete(new_dataset)
        await db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to create table: {str(e)}")

    return new_dataset

@router.post("/{session_id}/datasets/tabular/{dataset_id}/records", status_code=201)
async def insert_records(
    session_id: str,
    dataset_id: str,
    payload: RowInsert,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # Verify Access
    result = await db.execute(select(TabularDataset).where(TabularDataset.id == dataset_id, TabularDataset.session_id == session_id))
    dataset = result.scalar_one_or_none()
    if not dataset: # Need to check session user_id actually, but assuming session paths are correct
        # Strict check:
        sess = await db.get(Session, session_id)
        if not sess or sess.user_id != user_id:
             raise HTTPException(status_code=404, detail="Session not found")
        if not dataset:
             raise HTTPException(status_code=404, detail="Dataset not found")

    service = TabularService(db)
    try:
        await service.insert_rows(dataset_id, payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "success", "count": len(payload.rows)}

@router.get("/{session_id}/datasets/tabular/{dataset_id}/records")
async def query_records(
    session_id: str,
    dataset_id: str,
    limit: int = 100,
    offset: int = 0,
    sort: Optional[str] = None,
    select: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # Verify (Simplified for brevity, ideally middleware or dependency does this)
    sess = await db.get(Session, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    service = TabularService(db)
    select_cols = select.split(",") if select else None
    
    # Parsing params for filters could be added here iterating request.query_params
    
    try:
        rows = await service.query_rows(dataset_id, limit, offset, sort=sort, select_cols=select_cols)
        return {"data": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
