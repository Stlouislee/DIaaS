"""
Pytest configuration and shared fixtures for all tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from neo4j import AsyncGraphDatabase
import pytest_asyncio

from app.main import app
from app.core.database import Base, get_db
from app.core.neo4j_db import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.session import Session
from app.models.tabular import TabularDataset
from app.models.graph import GraphDataset


# Test database URL (in-memory SQLite for unit tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test user ID
TEST_USER_ID = "test-user-12345"
TEST_API_KEY = "test-api-key-67890"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    
    # Setup basic mock behavior
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_driver.session.return_value.__aexit__.return_value = None
    
    return mock_driver


@pytest.fixture
def override_get_db(test_db):
    """Override get_db dependency for testing."""
    async def _override_get_db():
        yield test_db
    return _override_get_db


@pytest.fixture
def override_get_neo4j_driver(mock_neo4j_driver):
    """Override get_neo4j_driver dependency for testing."""
    def _override_get_neo4j_driver():
        return mock_neo4j_driver
    return _override_get_neo4j_driver


@pytest.fixture
def override_get_current_user_id():
    """Override get_current_user_id dependency for testing."""
    async def _override_get_current_user_id():
        return TEST_USER_ID
    return _override_get_current_user_id


@pytest.fixture
async def test_client(
    override_get_db,
    override_get_neo4j_driver,
    override_get_current_user_id
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_neo4j_driver] = override_get_neo4j_driver
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sync_test_client():
    """Create a synchronous test client for simple tests."""
    return TestClient(app)


@pytest.fixture
async def test_session(test_db) -> Session:
    """Create a test session in the database."""
    session = Session(
        user_id=TEST_USER_ID,
        name="Test Session",
        description="Test session for unit tests"
    )
    test_db.add(session)
    await test_db.commit()
    await test_db.refresh(session)
    return session


@pytest.fixture
async def test_tabular_dataset(test_db, test_session) -> TabularDataset:
    """Create a test tabular dataset."""
    dataset = TabularDataset(
        session_id=test_session.id,
        name="test_dataset"
    )
    test_db.add(dataset)
    await test_db.commit()
    await test_db.refresh(dataset)
    return dataset


@pytest.fixture
async def test_graph_dataset(test_db, test_session) -> GraphDataset:
    """Create a test graph dataset."""
    dataset = GraphDataset(
        session_id=test_session.id,
        name="test_graph"
    )
    test_db.add(dataset)
    await test_db.commit()
    await test_db.refresh(dataset)
    return dataset


@pytest.fixture
def sample_tabular_schema():
    """Sample tabular dataset schema."""
    return {
        "name": "VARCHAR(255)",
        "age": "INTEGER",
        "email": "VARCHAR(255)"
    }


@pytest.fixture
def sample_tabular_rows():
    """Sample tabular dataset rows."""
    return [
        {"name": "Alice", "age": 30, "email": "alice@example.com"},
        {"name": "Bob", "age": 25, "email": "bob@example.com"},
        {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
    ]


@pytest.fixture
def sample_graph_node():
    """Sample graph node data."""
    return {
        "label": "Person",
        "properties": {
            "name": "Alice",
            "age": 30
        }
    }


@pytest.fixture
def sample_graph_edge():
    """Sample graph edge data."""
    return {
        "from_node_id": 1,
        "to_node_id": 2,
        "type": "KNOWS",
        "properties": {
            "since": "2020-01-01"
        }
    }


@pytest.fixture
def auth_headers():
    """Authentication headers for tests."""
    return {"X-API-Key": TEST_API_KEY}
