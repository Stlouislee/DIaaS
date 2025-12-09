from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_valid_session, get_valid_graph_dataset
from app.core.neo4j_db import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.graph import GraphDataset
from app.models.graph_schemas import GraphDatasetCreate, GraphDatasetResponse, NodeCreate, EdgeCreate
from app.services.graph_service import GraphService

router = APIRouter()

@router.post("/{session_id}/datasets/graph", response_model=GraphDatasetResponse, summary="Create Graph Dataset", description="Initialize a new empty graph dataset.")
async def create_graph_dataset(
    dataset_in: GraphDatasetCreate,
    session: Session = Depends(get_valid_session),
    db: AsyncSession = Depends(get_db)
):
    new_dataset = GraphDataset(
        session_id=session.id,
        name=dataset_in.name
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    return new_dataset

@router.post("/{session_id}/datasets/graph/{dataset_id}/nodes", summary="Create Node", description="Add a new node to the graph.")
async def create_node(
    node: NodeCreate,
    dataset: GraphDataset = Depends(get_valid_graph_dataset),
    driver = Depends(get_neo4j_driver)
):
    service = GraphService(driver)
    return await service.create_node(dataset.id, node.label, node.properties)

@router.post("/{session_id}/datasets/graph/{dataset_id}/edges", summary="Create Edge", description="Create a relationship between two nodes.")
async def create_edge(
    edge: EdgeCreate,
    dataset: GraphDataset = Depends(get_valid_graph_dataset),
    driver = Depends(get_neo4j_driver)
):
    service = GraphService(driver)
    res = await service.create_relationship(dataset.id, edge.from_node_id, edge.to_node_id, edge.type, edge.properties)
    if not res:
        raise HTTPException(status_code=400, detail="Could not create edge. Check node IDs.")
    return res

@router.get("/{session_id}/datasets/graph/{dataset_id}/nodes", summary="List Nodes", description="Retrieve nodes from the graph, optionally filtered by label.")
async def list_nodes(
    label: Optional[str] = None,
    limit: int = 100,
    dataset: GraphDataset = Depends(get_valid_graph_dataset),
    driver = Depends(get_neo4j_driver)
):
    service = GraphService(driver)
    return await service.get_nodes(dataset.id, label, limit)

@router.get("/{session_id}/datasets/graph/{dataset_id}/nodes/{node_id}/neighbors")
async def get_neighbors(
    node_id: int,
    dataset: GraphDataset = Depends(get_valid_graph_dataset),
    driver = Depends(get_neo4j_driver)
):
    service = GraphService(driver)
    return await service.get_neighbors(dataset.id, node_id)

@router.post("/{session_id}/datasets/graph/{dataset_id}/algorithms/shortest_path", summary="Find Shortest Path", description="Calculate the shortest path between two nodes using Neo4j algorithms.")
async def shortest_path(
    from_id: int,
    to_id: int,
    dataset: GraphDataset = Depends(get_valid_graph_dataset),
    driver = Depends(get_neo4j_driver)
):
    service = GraphService(driver)
    path = await service.shortest_path(dataset.id, from_id, to_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path found.")
    return path
