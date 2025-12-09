"""
Unit tests for dependency injection functions.
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_valid_session,
    get_valid_tabular_dataset,
    get_valid_graph_dataset
)
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.graph import GraphDataset


pytestmark = pytest.mark.unit


class TestGetValidSession:
    """Tests for get_valid_session dependency."""
    
    async def test_valid_session_returns_session(self, test_db, test_session):
        """Test that valid session is returned."""
        result = await get_valid_session(
            session_id=test_session.id,
            user_id=test_session.user_id,
            db=test_db
        )
        
        assert result.id == test_session.id
        assert result.user_id == test_session.user_id
    
    async def test_nonexistent_session_raises_404(self, test_db):
        """Test that nonexistent session raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            await get_valid_session(
                session_id="nonexistent-id",
                user_id="test-user",
                db=test_db
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    async def test_wrong_user_raises_404(self, test_db, test_session):
        """Test that accessing another user's session raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            await get_valid_session(
                session_id=test_session.id,
                user_id="wrong-user-id",
                db=test_db
            )
        
        assert exc_info.value.status_code == 404


class TestGetValidTabularDataset:
    """Tests for get_valid_tabular_dataset dependency."""
    
    async def test_valid_dataset_returns_dataset(
        self, test_db, test_session, test_tabular_dataset
    ):
        """Test that valid dataset is returned."""
        result = await get_valid_tabular_dataset(
            session_id=test_session.id,
            dataset_id=test_tabular_dataset.id,
            user_id=test_session.user_id,
            db=test_db
        )
        
        assert result.id == test_tabular_dataset.id
        assert result.session_id == test_session.id
    
    async def test_nonexistent_dataset_raises_404(self, test_db, test_session):
        """Test that nonexistent dataset raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            await get_valid_tabular_dataset(
                session_id=test_session.id,
                dataset_id="nonexistent-id",
                user_id=test_session.user_id,
                db=test_db
            )
        
        assert exc_info.value.status_code == 404
    
    async def test_wrong_session_raises_404(
        self, test_db, test_session, test_tabular_dataset
    ):
        """Test that dataset from wrong session raises 404."""
        # Create another session
        other_session = Session(user_id="other-user", name="Other Session")
        test_db.add(other_session)
        await test_db.commit()
        await test_db.refresh(other_session)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_valid_tabular_dataset(
                session_id=other_session.id,
                dataset_id=test_tabular_dataset.id,
                user_id=other_session.user_id,
                db=test_db
            )
        
        assert exc_info.value.status_code == 404


class TestGetValidGraphDataset:
    """Tests for get_valid_graph_dataset dependency."""
    
    async def test_valid_dataset_returns_dataset(
        self, test_db, test_session, test_graph_dataset
    ):
        """Test that valid graph dataset is returned."""
        result = await get_valid_graph_dataset(
            session_id=test_session.id,
            dataset_id=test_graph_dataset.id,
            user_id=test_session.user_id,
            db=test_db
        )
        
        assert result.id == test_graph_dataset.id
        assert result.session_id == test_session.id
    
    async def test_nonexistent_dataset_raises_404(self, test_db, test_session):
        """Test that nonexistent graph dataset raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            await get_valid_graph_dataset(
                session_id=test_session.id,
                dataset_id="nonexistent-id",
                user_id=test_session.user_id,
                db=test_db
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
