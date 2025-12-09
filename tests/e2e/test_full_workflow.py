"""
End-to-End Tests: Full Application Workflow
Tests the complete user journey through the API
"""
import pytest
import requests
import uuid


class TestCompleteWorkflow:
    """Test complete workflow from registration to data export"""
    
    def test_health_check(self, api_base_url):
        """Test API health endpoint"""
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_user_registration(self, api_base_url):
        """Test user registration"""
        response = requests.post(f"{api_base_url}/api/v1/users/register")
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert "user_id" in data
        assert len(data["api_key"]) >= 8
    
    def test_session_lifecycle(self, api_base_url, auth_headers):
        """Test session creation, retrieval, and deletion"""
        # Create session
        session_data = {
            "name": f"Test Session {uuid.uuid4()}",
            "description": "E2E test session"
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/",
            json=session_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        session = response.json()
        session_id = session["id"]
        assert session["name"] == session_data["name"]
        assert session["tabular_datasets"] == []
        assert session["graph_datasets"] == []
        
        # Get session
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == session_id
        
        # List sessions
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/",
            headers=auth_headers
        )
        assert response.status_code == 200
        sessions = response.json()
        assert any(s["id"] == session_id for s in sessions)
        
        # Delete session
        response = requests.delete(
            f"{api_base_url}/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify deletion
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestTabularDataWorkflow:
    """Test complete tabular data workflow"""
    
    def test_tabular_dataset_crud(self, api_base_url, auth_headers, session_id):
        """Test tabular dataset creation, data insertion, and querying"""
        # Create tabular dataset
        dataset_data = {
            "name": "users",
            "schema_def": {
                "name": "VARCHAR(100)",
                "age": "INTEGER",
                "email": "VARCHAR(255)"
            }
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular",
            json=dataset_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        dataset = response.json()
        dataset_id = dataset["id"]
        assert dataset["name"] == "users"
        
        # Insert records
        records = {
            "rows": [
                {"name": "Alice", "age": 30, "email": "alice@example.com"},
                {"name": "Bob", "age": 25, "email": "bob@example.com"},
                {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
            ]
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            json=records,
            headers=auth_headers
        )
        assert response.status_code == 201
        result = response.json()
        assert result["status"] == "success"
        assert result["count"] == 3
        
        # Query records
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["data"]) == 3
        
        # Query with filters
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            params={"limit": 2, "sort": "age:desc"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["data"][0]["age"] >= data["data"][1]["age"]
        
        # Query with selection
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            params={"select": "name,age"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for row in data["data"]:
            assert "name" in row
            assert "age" in row
    
    def test_sql_query_execution(self, api_base_url, auth_headers, session_id):
        """Test raw SQL query execution"""
        # Create and populate dataset
        dataset_data = {
            "name": "products",
            "schema_def": {"name": "VARCHAR(100)", "price": "DECIMAL(10,2)"}
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular",
            json=dataset_data,
            headers=auth_headers
        )
        dataset_id = response.json()["id"]
        
        # Insert data
        requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            json={"rows": [
                {"name": "Product A", "price": 10.99},
                {"name": "Product B", "price": 20.99}
            ]},
            headers=auth_headers
        )
        
        # Execute SQL query
        table_name = f"dataset_{dataset_id.replace('-', '_')}"
        query_data = {
            "query": f'SELECT name, price FROM "{table_name}" WHERE price > 15',
            "type": "sql",
            "params": {}
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/query",
            json=query_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Product B"


class TestGraphDataWorkflow:
    """Test complete graph data workflow"""
    
    def test_graph_dataset_operations(self, api_base_url, auth_headers, session_id):
        """Test graph dataset creation and node/edge operations"""
        # Create graph dataset
        dataset_data = {"name": "social_network"}
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph",
            json=dataset_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        dataset = response.json()
        dataset_id = dataset["id"]
        
        # Create nodes
        node1_data = {
            "label": "Person",
            "properties": {"name": "Alice", "age": 30}
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
            json=node1_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        node1 = response.json()
        node1_id = node1["_id"]
        
        node2_data = {
            "label": "Person",
            "properties": {"name": "Bob", "age": 25}
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
            json=node2_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        node2 = response.json()
        node2_id = node2["_id"]
        
        # Create edge
        edge_data = {
            "from_node_id": node1_id,
            "to_node_id": node2_id,
            "type": "KNOWS",
            "properties": {"since": "2020"}
        }
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/edges",
            json=edge_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # List nodes
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
            headers=auth_headers
        )
        assert response.status_code == 200
        nodes = response.json()
        assert len(nodes) >= 2
        
        # Get neighbors
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes/{node1_id}/neighbors",
            headers=auth_headers
        )
        assert response.status_code == 200
        neighbors = response.json()
        assert len(neighbors) >= 1
        assert neighbors[0]["type"] == "KNOWS"
    
    def test_shortest_path(self, api_base_url, auth_headers, session_id):
        """Test shortest path algorithm"""
        # Create graph
        dataset_data = {"name": "path_graph"}
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph",
            json=dataset_data,
            headers=auth_headers
        )
        dataset_id = response.json()["id"]
        
        # Create chain of nodes: A -> B -> C
        nodes = []
        for name in ["A", "B", "C"]:
            response = requests.post(
                f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes",
                json={"label": "Node", "properties": {"name": name}},
                headers=auth_headers
            )
            nodes.append(response.json()["_id"])
        
        # Create edges
        for i in range(len(nodes) - 1):
            requests.post(
                f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/edges",
                json={
                    "from_node_id": nodes[i],
                    "to_node_id": nodes[i + 1],
                    "type": "CONNECTS",
                    "properties": {}
                },
                headers=auth_headers
            )
        
        # Find shortest path
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/algorithms/shortest_path",
            params={"from_id": nodes[0], "to_id": nodes[2]},
            headers=auth_headers
        )
        assert response.status_code == 200
        path = response.json()
        assert path["length"] == 2  # A -> B -> C
        assert len(path["nodes"]) == 3


class TestExportWorkflow:
    """Test data export functionality"""
    
    def test_session_export(self, api_base_url, auth_headers, session_id):
        """Test complete session export"""
        # Create tabular dataset
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular",
            json={
                "name": "export_test",
                "schema_def": {"name": "VARCHAR(100)", "value": "INTEGER"}
            },
            headers=auth_headers
        )
        dataset_id = response.json()["id"]
        
        # Insert data
        requests.post(
            f"{api_base_url}/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records",
            json={"rows": [{"name": "test", "value": 123}]},
            headers=auth_headers
        )
        
        # Export session
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}/export",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert len(response.content) > 0


class TestSecurityAndAuthorization:
    """Test security and authorization"""
    
    def test_unauthorized_access(self, api_base_url):
        """Test that endpoints require authentication"""
        # Try to list sessions without auth
        response = requests.get(f"{api_base_url}/api/v1/sessions/")
        assert response.status_code == 403
    
    def test_invalid_api_key(self, api_base_url):
        """Test invalid API key is rejected"""
        headers = {"X-API-Key": "invalid-key"}
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/",
            headers=headers
        )
        assert response.status_code == 403
    
    def test_cross_user_access_prevention(self, api_base_url):
        """Test that users cannot access other users' data"""
        # Create first user
        response1 = requests.post(f"{api_base_url}/api/v1/users/register")
        api_key1 = response1.json()["api_key"]
        headers1 = {"X-API-Key": api_key1}
        
        # Create second user
        response2 = requests.post(f"{api_base_url}/api/v1/users/register")
        api_key2 = response2.json()["api_key"]
        headers2 = {"X-API-Key": api_key2}
        
        # User 1 creates a session
        response = requests.post(
            f"{api_base_url}/api/v1/sessions/",
            json={"name": "User 1 Session"},
            headers=headers1
        )
        session_id = response.json()["id"]
        
        # User 2 tries to access User 1's session
        response = requests.get(
            f"{api_base_url}/api/v1/sessions/{session_id}",
            headers=headers2
        )
        assert response.status_code == 404  # Should not find it
