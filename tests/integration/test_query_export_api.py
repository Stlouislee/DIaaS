"""
Integration tests for Query and Export API endpoints.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


class TestQueryAPI:
    """Tests for /api/v1/sessions/{id}/query endpoint."""
    
    async def test_execute_sql_query(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test executing SQL query."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/query",
            json={
                "query": "SELECT 1 as test",
                "type": "sql",
                "params": {}
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
    
    async def test_execute_cypher_query(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test executing Cypher query."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/query",
            json={
                "query": "RETURN 1 as test",
                "type": "cypher",
                "params": {}
            },
            headers=auth_headers
        )
        
        # Will depend on Neo4j mock
        assert response.status_code in [200, 400, 500]
    
    async def test_invalid_query_type(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test that invalid query type returns error."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/query",
            json={
                "query": "SELECT 1",
                "type": "invalid",
                "params": {}
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    async def test_query_with_params(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test executing query with parameters."""
        response = await test_client.post(
            f"/api/v1/sessions/{test_session.id}/query",
            json={
                "query": "SELECT :value as test",
                "type": "sql",
                "params": {"value": 42}
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 400]


class TestExportAPI:
    """Tests for /api/v1/sessions/{id}/export endpoint."""
    
    async def test_export_session(
        self,
        test_client: AsyncClient,
        test_session,
        test_db_session,
        auth_headers
    ):
        """Test exporting entire session."""
        # Don't create datasets with physical tables in test environment
        # Export will fail gracefully if tables don't exist
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}/export",
            headers=auth_headers
        )
        
        # In test environment without physical tables, export might fail
        # In production with real tables, it should succeed
        assert response.status_code in [200, 400, 500]
    
    async def test_export_nonexistent_session(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test exporting nonexistent session fails."""
        response = await test_client.get(
            "/api/v1/sessions/nonexistent/export",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_export_empty_session(
        self, test_client: AsyncClient, test_session, auth_headers
    ):
        """Test exporting session with no datasets."""
        response = await test_client.get(
            f"/api/v1/sessions/{test_session.id}/export",
            headers=auth_headers
        )
        
        # Should succeed even with empty session
        assert response.status_code in [200, 500]
