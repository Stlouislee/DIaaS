from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.neo4j_db import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.graph import GraphDataset
from app.models.graph_schemas import GraphDatasetCreate, GraphDatasetResponse, NodeCreate, EdgeCreate
from app.services.graph_service import GraphService

router = APIRouter()

async def get_valid_dataset(
    session_id: str, 
    dataset_id: str, 
    user_id: str, 
    db: AsyncSession
) -> GraphDataset:
    sess = await db.get(Session, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = await db.execute(select(GraphDataset).where(GraphDataset.id == dataset_id, GraphDataset.session_id == session_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Graph Dataset not found")
    return dataset

@router.post("/{session_id}/datasets/graph", response_model=GraphDatasetResponse, summary="Create Graph Dataset", description="Initialize a new empty graph dataset.")
async def create_graph_dataset(
    session_id: str,
    dataset_in: GraphDatasetCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    new_dataset = GraphDataset(
        session_id=session_id,
        name=dataset_in.name
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    return new_dataset

@router.post("/{session_id}/datasets/graph/{dataset_id}/nodes", summary="Create Node", description="Add a new node to the graph.")
async def create_node(
    session_id: str,
    dataset_id: str,
    node: NodeCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    await get_valid_dataset(session_id, dataset_id, user_id, db)
    service = GraphService(driver)
    return await service.create_node(dataset_id, node.label, node.properties)

@router.post("/{session_id}/datasets/graph/{dataset_id}/edges", summary="Create Edge", description="Create a relationship between two nodes.")
async def create_edge(
    session_id: str,
    dataset_id: str,
    edge: EdgeCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    await get_valid_dataset(session_id, dataset_id, user_id, db)
    service = GraphService(driver)
    res = await service.create_relationship(dataset_id, edge.from_node_id, edge.to_node_id, edge.type, edge.properties)
    if not res:
        raise HTTPException(status_code=400, detail="Could not create edge. Check node IDs.")
    return res

@router.get("/{session_id}/datasets/graph/{dataset_id}/nodes", summary="List Nodes", description="Retrieve nodes from the graph, optionally filtered by label.")
async def list_nodes(
    session_id: str,
    dataset_id: str,
    label: Optional[str] = None,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    await get_valid_dataset(session_id, dataset_id, user_id, db)
    service = GraphService(driver)
    return await service.get_nodes(dataset_id, label, limit)

@router.get("/{session_id}/datasets/graph/{dataset_id}/nodes/{node_id}/neighbors")
async def get_neighbors(
    session_id: str,
    dataset_id: str,
    node_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    await get_valid_dataset(session_id, dataset_id, user_id, db)
    service = GraphService(driver)
    return await service.get_neighbors(dataset_id, node_id)

@router.post("/{session_id}/datasets/graph/{dataset_id}/algorithms/shortest_path", summary="Find Shortest Path", description="Calculate the shortest path between two nodes using Neo4j algorithms.")
async def shortest_path(
    session_id: str,
    dataset_id: str,
    from_id: int,
    to_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    driver = Depends(get_neo4j_driver)
):
    await get_valid_dataset(session_id, dataset_id, user_id, db)
    service = GraphService(driver)
    path = await service.shortest_path(dataset_id, from_id, to_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path found.")
    return path
