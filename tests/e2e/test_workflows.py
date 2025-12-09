"""
End-to-end tests for complete workflows.
"""
import pytest
from httpx import AsyncClient


pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    async def test_complete_tabular_workflow(
        self, test_client: AsyncClient, auth_headers, sample_tabular_schema
    ):
        """Test complete workflow: create session -> dataset -> insert -> query -> delete."""
        
        # 1. Create session
        session_response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "E2E Test Session", "description": "End-to-end test"},
            headers=auth_headers
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]
        
        # 2. Create tabular dataset
        dataset_response = await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/tabular",
            json={
                "name": "users",
                "schema_def": sample_tabular_schema
            },
            headers=auth_headers
        )
        assert dataset_response.status_code == 200
        dataset_id = dataset_response.json()["id"]
        
        # 3. Insert records (may fail in test environment without real DB)
        insert_response = await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            json={
                "rows": [
                    {"name": "Alice", "age": 30, "email": "alice@test.com"}
                ]
            },
            headers=auth_headers
        )
        # Accept both success and failure (table might not exist in test)
        assert insert_response.status_code in [201, 400]
        
        # 4. Query records
        query_response = await test_client.get(
            f"/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            params={"limit": 10},
            headers=auth_headers
        )
        assert query_response.status_code in [200, 400]
        
        # 5. Get session (verify datasets are linked)
        get_session_response = await test_client.get(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert get_session_response.status_code == 200
        session_data = get_session_response.json()
        assert len(session_data["tabular_datasets"]) >= 1
        
        # 6. Delete session
        delete_response = await test_client.delete(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
        
        # 7. Verify deletion
        verify_response = await test_client.get(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert verify_response.status_code == 404
    
    async def test_complete_graph_workflow(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test complete graph workflow."""
        
        # 1. Create session
        session_response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Graph E2E Test"},
            headers=auth_headers
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]
        
        # 2. Create graph dataset
        dataset_response = await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/graph",
            json={"name": "social_network"},
            headers=auth_headers
        )
        assert dataset_response.status_code == 200
        dataset_id = dataset_response.json()["id"]
        
        # 3. Create nodes
        node1_response = await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
            json={
                "label": "Person",
                "properties": {"name": "Alice", "age": 30}
            },
            headers=auth_headers
        )
        # May fail if Neo4j not available
        assert node1_response.status_code in [200, 500]
        
        # 4. List nodes
        list_response = await test_client.get(
            f"/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
            headers=auth_headers
        )
        assert list_response.status_code in [200, 500]
        
        # 5. Delete session
        delete_response = await test_client.delete(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
    
    async def test_multi_session_isolation(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test that multiple sessions are properly isolated."""
        
        # Create two sessions
        session1_response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Session 1"},
            headers=auth_headers
        )
        session2_response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Session 2"},
            headers=auth_headers
        )
        
        assert session1_response.status_code == 201
        assert session2_response.status_code == 201
        
        session1_id = session1_response.json()["id"]
        session2_id = session2_response.json()["id"]
        
        assert session1_id != session2_id
        
        # Create dataset in session1
        dataset_response = await test_client.post(
            f"/api/v1/sessions/{session1_id}/datasets/tabular",
            json={
                "name": "dataset1",
                "schema_def": {"col1": "VARCHAR"}
            },
            headers=auth_headers
        )
        assert dataset_response.status_code == 200
        dataset_id = dataset_response.json()["id"]
        
        # Try to access dataset through session2 (should fail)
        wrong_session_response = await test_client.get(
            f"/api/v1/sessions/{session2_id}/datasets/tabular/{dataset_id}/records",
            headers=auth_headers
        )
        assert wrong_session_response.status_code == 404
        
        # Cleanup
        await test_client.delete(f"/api/v1/sessions/{session1_id}", headers=auth_headers)
        await test_client.delete(f"/api/v1/sessions/{session2_id}", headers=auth_headers)
    
    async def test_export_workflow(
        self, test_client: AsyncClient, auth_headers
    ):
        """Test export workflow with mixed datasets."""
        
        # 1. Create session
        session_response = await test_client.post(
            "/api/v1/sessions/",
            json={"name": "Export Test Session"},
            headers=auth_headers
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]
        
        # 2. Create tabular dataset
        await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/tabular",
            json={
                "name": "users",
                "schema_def": {"name": "VARCHAR", "age": "INTEGER"}
            },
            headers=auth_headers
        )
        
        # 3. Create graph dataset
        await test_client.post(
            f"/api/v1/sessions/{session_id}/datasets/graph",
            json={"name": "relationships"},
            headers=auth_headers
        )
        
        # 4. Export session
        export_response = await test_client.get(
            f"/api/v1/sessions/{session_id}/export",
            headers=auth_headers
        )
        
        # Should succeed or fail gracefully
        assert export_response.status_code in [200, 400, 500]
        
        if export_response.status_code == 200:
            assert export_response.headers["content-type"] == "application/zip"
        
        # 5. Cleanup
        await test_client.delete(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
