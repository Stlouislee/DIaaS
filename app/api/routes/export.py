from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.neo4j_db import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.graph import GraphDataset
from app.services.tabular_service import TabularService
from app.services.graph_service import GraphService
from app.services.export_service import ExportService

router = APIRouter()

@router.get("/{session_id}/export")
async def export_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    # Verify Session
    sess = await db.get(Session, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    files = {}

    # 1. Export Tabular Datasets
    result = await db.execute(select(TabularDataset).where(TabularDataset.session_id == session_id))
    tabular_datasets = result.scalars().all()
    
    t_service = TabularService(db)
    for tds in tabular_datasets:
        data = await t_service.query_rows(tds.id, limit=100000) # Cap for safety
        csv_content = ExportService.tabular_to_csv(data)
        files[f"{tds.name}.csv"] = csv_content

    # 2. Export Graph Datasets
    # Getting all graph data is heavy. We will dump nodes and relations as JSON.
    result = await db.execute(select(GraphDataset).where(GraphDataset.session_id == session_id))
    graph_datasets = result.scalars().all()
    
    g_service = GraphService(driver)
    for gds in graph_datasets:
        nodes = await g_service.get_nodes(gds.id, limit=10000)
        # Getting all edges is tricky without bulk export. 
        # For prototype, we skip full edge dump to avoid timeout, or do basic neighborhood of fetched nodes.
        # Let's dump the nodes we found.
        json_content = ExportService.graph_to_json(nodes, [])
        files[f"{gds.name}.json"] = json_content

    zip_bytes = ExportService.create_zip(files)
    
    return Response(
        content=zip_bytes, 
        media_type="application/zip", 
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}.zip"}
    )
