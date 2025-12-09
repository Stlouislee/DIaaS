"""
Test utilities and helper functions.
"""
import asyncio
from typing import Dict, Any, List
import secrets


def generate_test_api_key() -> str:
    """Generate a valid test API key."""
    return secrets.token_urlsafe(32)


def create_sample_session_data(name: str = "Test Session") -> Dict[str, Any]:
    """Create sample session data for testing."""
    return {
        "name": name,
        "description": f"Test session: {name}"
    }


def create_sample_tabular_schema(
    columns: List[str] = None
) -> Dict[str, str]:
    """Create sample tabular schema."""
    if columns is None:
        columns = ["id", "name", "value"]
    
    type_map = {
        "id": "INTEGER",
        "name": "VARCHAR(255)",
        "value": "VARCHAR(255)",
        "age": "INTEGER",
        "email": "VARCHAR(255)",
        "created_at": "TIMESTAMP"
    }
    
    return {col: type_map.get(col, "VARCHAR(255)") for col in columns}


def create_sample_rows(count: int = 3) -> List[Dict[str, Any]]:
    """Create sample data rows."""
    return [
        {
            "name": f"User {i}",
            "age": 20 + i,
            "email": f"user{i}@test.com"
        }
        for i in range(count)
    ]


async def wait_for_condition(
    condition_func,
    timeout: float = 5.0,
    interval: float = 0.1
) -> bool:
    """Wait for a condition to become true."""
    elapsed = 0.0
    while elapsed < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def session(user_id: str, name: str = "Test Session") -> Dict[str, Any]:
        """Create session test data."""
        return {
            "user_id": user_id,
            "name": name,
            "description": f"Test session for {user_id}"
        }
    
    @staticmethod
    def tabular_dataset(session_id: str, name: str = "test_dataset") -> Dict[str, Any]:
        """Create tabular dataset test data."""
        return {
            "session_id": session_id,
            "name": name
        }
    
    @staticmethod
    def graph_dataset(session_id: str, name: str = "test_graph") -> Dict[str, Any]:
        """Create graph dataset test data."""
        return {
            "session_id": session_id,
            "name": name
        }
    
    @staticmethod
    def graph_node(label: str = "TestNode", **properties) -> Dict[str, Any]:
        """Create graph node test data."""
        return {
            "label": label,
            "properties": properties or {"name": "test"}
        }
    
    @staticmethod
    def graph_edge(from_id: int, to_id: int, rel_type: str = "TEST") -> Dict[str, Any]:
        """Create graph edge test data."""
        return {
            "from_node_id": from_id,
            "to_node_id": to_id,
            "type": rel_type,
            "properties": {}
        }
