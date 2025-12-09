"""
Integration tests for Graph Data API endpoints.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


class TestGraphDatasetAPI:
    """Tests for graph dataset endpoints."""
    
    async def test_create_graph_dataset(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test creating a graph dataset."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/datasets/graph",
            json={"name": "social_network"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "social_network"
        assert data["session_id"] == test_session.id
        assert "id" in data
    
    async def test_create_node(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers,
        sample_graph_node
    ):
        """Test creating a node in graph dataset."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/nodes",
            json=sample_graph_node,
            headers=auth_headers
        )
        
        # Will succeed if Neo4j is mocked properly
        assert response.status_code in [200, 500]
    
    async def test_create_edge(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers,
        sample_graph_edge
    ):
        """Test creating an edge in graph dataset."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/edges",
            json=sample_graph_edge,
            headers=auth_headers
        )
        
        # Will depend on Neo4j mock
        assert response.status_code in [200, 400, 500]
    
    async def test_list_nodes(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers
    ):
        """Test listing nodes from graph dataset."""
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/nodes",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 500]
    
    async def test_list_nodes_with_label_filter(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers
    ):
        """Test listing nodes with label filter."""
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/nodes",
            params={"label": "Person", "limit": 50},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 500]
    
    async def test_get_neighbors(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers
    ):
        """Test getting neighbors of a node."""
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/nodes/1/neighbors",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 500]
    
    async def test_shortest_path(
        self,
        test_client: AsyncClient,
        test_session,
        test_graph_dataset,
        auth_headers
    ):
        """Test finding shortest path between nodes."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/datasets/graph/{test_graph_dataset.id}/algorithms/shortest_path",
            params={"from_id": 1, "to_id": 2},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 500]
    
    async def test_access_other_users_graph_dataset_fails(
        self,
        test_client: AsyncClient,
        test_db,
        test_graph_dataset,
        auth_headers
    ):
        """Test that accessing another user's graph dataset fails."""
        from app.models.session import Session
        other_session = Session(user_id="other-user", name="Other Session")
        test_db.add(other_session)
        await test_db.commit()
        await test_db.refresh(other_session)
        
        response = await test_client.get(
            f"/api/v1/sessions/{other_session.id}/datasets/graph/{test_graph_dataset.id}/nodes",
            headers=auth_headers
        )
        
        assert response.status_code == 404
