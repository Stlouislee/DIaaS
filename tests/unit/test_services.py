"""
Unit tests for service layer.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tabular_service import TabularService
from app.services.graph_service import GraphService
from app.services.export_service import ExportService


pytestmark = pytest.mark.unit


class TestTabularService:
    """Tests for TabularService."""
    
    def test_get_table_name(self):
        """Test table name generation."""
        mock_db = MagicMock()
        service = TabularService(mock_db)
        
        dataset_id = "abc-123-def"
        table_name = service._get_table_name(dataset_id)
        
        assert table_name == "dataset_abc_123_def"
        assert "-" not in table_name
    
    async def test_create_table_generates_correct_sql(self):
        """Test that create_table generates correct SQL."""
        mock_db = AsyncMock()
        service = TabularService(mock_db)
        
        dataset_id = "test-123"
        schema = {
            "name": "VARCHAR(255)",
            "age": "INTEGER"
        }
        
        await service.create_table(dataset_id, schema)
        
        # Verify execute was called
        assert mock_db.execute.called
        # Verify commit was called
        assert mock_db.commit.called
    
    async def test_insert_rows_with_empty_list(self):
        """Test that insert_rows handles empty list."""
        mock_db = AsyncMock()
        service = TabularService(mock_db)
        
        await service.insert_rows("test-id", [])
        
        # Should return early without calling execute
        assert not mock_db.execute.called


class TestGraphService:
    """Tests for GraphService."""
    
    def test_get_dataset_label(self):
        """Test dataset label generation."""
        mock_driver = MagicMock()
        service = GraphService(mock_driver)
        
        dataset_id = "abc-123-def"
        label = service._get_dataset_label(dataset_id)
        
        assert label == "Graph_abc_123_def"
        assert "-" not in label
    
    async def test_create_node_calls_driver(self):
        """Test that create_node calls Neo4j driver."""
        mock_driver = MagicMock()
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_record = {"n": {"id": 1, "name": "Test"}}
        
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__aenter__.return_value = mock_session
        
        service = GraphService(mock_driver)
        
        result = await service.create_node(
            "dataset-123",
            "Person",
            {"name": "Alice"}
        )
        
        assert mock_session.run.called
        assert result == mock_record["n"]


class TestExportService:
    """Tests for ExportService."""
    
    def test_tabular_to_csv_empty_data(self):
        """Test CSV export with empty data."""
        result = ExportService.tabular_to_csv([])
        assert result == ""
    
    def test_tabular_to_csv_with_data(self):
        """Test CSV export with data."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        
        result = ExportService.tabular_to_csv(data)
        
        assert "name,age" in result
        assert "Alice,30" in result
        assert "Bob,25" in result
    
    def test_tabular_to_json_with_data(self):
        """Test JSON export."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        
        result = ExportService.tabular_to_json(data)
        
        assert "Alice" in result
        assert "Bob" in result
        assert '"age": 30' in result or '"age":30' in result
    
    def test_graph_to_json(self):
        """Test graph JSON export."""
        nodes = [{"id": 1, "name": "Alice"}]
        edges = [{"from": 1, "to": 2, "type": "KNOWS"}]
        
        result = ExportService.graph_to_json(nodes, edges)
        
        assert "nodes" in result
        assert "links" in result
        assert "Alice" in result
    
    def test_create_zip(self):
        """Test ZIP file creation."""
        files = {
            "file1.txt": "content1",
            "file2.txt": "content2"
        }
        
        result = ExportService.create_zip(files)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
