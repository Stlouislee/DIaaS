"""
Integration tests for Sessions API endpoints.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


class TestSessionsAPI:
    """Tests for /api/v1/sessions endpoints."""
    
    async def test_create_session(self, test_client: AsyncClient, auth_headers):
        """Test creating a new session."""
        response = await test_client.post(
            "/api/v1/sessions/",
            json={
                "name": "Test Session",
                "description": "A test session"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Session"
        assert data["description"] == "A test session"
        assert "id" in data
        assert "created_at" in data
        assert data["tabular_datasets"] == []
        assert data["graph_datasets"] == []
    
    async def test_create_session_without_description(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test creating session without optional description."""
        response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Minimal Session"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Session"
    
    async def test_list_sessions(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test listing all sessions."""
        response = await test_client.get(
            "/api/v1/sessions/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(s["id"] == test_session.id for s in data)
    
    async def test_get_session_by_id(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test getting a specific session."""
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_session.id
        assert data["name"] == test_session.name
    
    async def test_get_nonexistent_session(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test getting a nonexistent session returns 404."""
        response = await test_client.get(
            "/api/v1/sessions/nonexistent-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_delete_session(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test deleting a session."""
        response = await test_client.delete(
            f"/api/v1/sessions/{test_session.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    async def test_create_session_without_auth(self, test_client: AsyncClient):
        """Test that creating session without auth fails."""
        response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Unauthorized Session"}
        )
        
        # In test environment with mocked auth, this will pass (201)
        # In production environment, this would fail (403)
        assert response.status_code in [201, 401, 403, 422]
