"""
Integration tests for Users API endpoints.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.integration


class TestUsersAPI:
    """Tests for /api/v1/users endpoints."""
    
    async def test_register_user(self, test_client: AsyncClient):
        """Test user registration."""
        response = await test_client.post("/api/v1/users/register")
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "api_key" in data
        assert "message" in data
        assert data["user_id"] == data["api_key"]
        assert len(data["api_key"]) >= 8
    
    async def test_register_generates_unique_keys(self, test_client: AsyncClient):
        """Test that each registration generates unique keys."""
        response1 = await test_client.post("/api/v1/users/register")
        response2 = await test_client.post("/api/v1/users/register")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        key1 = response1.json()["api_key"]
        key2 = response2.json()["api_key"]
        
        assert key1 != key2
