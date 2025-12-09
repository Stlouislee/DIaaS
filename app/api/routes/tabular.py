from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_valid_session, get_valid_tabular_dataset
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.tabular_schemas import TabularDatasetCreate, TabularDatasetResponse, RowInsert
from app.services.tabular_service import TabularService
from typing import Optional, List

router = APIRouter()

@router.post("/{session_id}/datasets/tabular", response_model=TabularDatasetResponse, summary="Create Tabular Dataset", description="Define a new tabular dataset with a specific schema.")
async def create_tabular_dataset(
    dataset_in: TabularDatasetCreate,
    session: Session = Depends(get_valid_session),
    db: AsyncSession = Depends(get_db)
):
    # Create Metadata
    session_id = session.id
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

@router.post("/{session_id}/datasets/tabular/{dataset_id}/records", status_code=201, summary="Insert Records", description="Insert multiple rows into a tabular dataset.")
async def insert_records(
    payload: RowInsert,
    dataset: TabularDataset = Depends(get_valid_tabular_dataset),
    db: AsyncSession = Depends(get_db)
):
    service = TabularService(db)
    try:
        await service.insert_rows(dataset.id, payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "success", "count": len(payload.rows)}

@router.get("/{session_id}/datasets/tabular/{dataset_id}/records", summary="Query Records", description="Retrieve rows from a dataset with optional filtering and sorting.")
async def query_records(
    limit: int = 100,
    offset: int = 0,
    sort: Optional[str] = None,
    select: Optional[str] = None,
    dataset: TabularDataset = Depends(get_valid_tabular_dataset),
    db: AsyncSession = Depends(get_db)
):
    service = TabularService(db)
    select_cols = select.split(",") if select else None
    
    # Parsing params for filters could be added here iterating request.query_params
    
    try:
        rows = await service.query_rows(dataset.id, limit, offset, sort=sort, select_cols=select_cols)
        return {"data": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
