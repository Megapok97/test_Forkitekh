import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from app.main import app
from app.database import get_db
from app.models import Base, Request
from datetime import datetime, UTC


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Specifies the backend for pytest-asyncio.

    Returns:
        str: The name of the asyncio backend.
    """
    return "asyncio"


@pytest.fixture(scope="module")
async def async_engine():
    """
    Creates an in-memory SQLite async engine for testing.

    Yields:
        AsyncEngine: SQLAlchemy async engine.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine):
    """
    Provides an async SQLAlchemy session for tests with a clean database state.

    Yields:
        AsyncSession: A new async session for database operations.
    """
    async_session = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        # Clear the requests table before each test
        await session.execute(text("DELETE FROM requests"))
        await session.commit()
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(async_session):
    """
    Provides a FastAPI TestClient with mocked database dependency.

    Args:
        async_session: The async SQLAlchemy session fixture.

    Yields:
        TestClient: FastAPI test client for sending HTTP requests.
    """

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_request():
    """
    Provides a sample Request object for testing.

    Returns:
        Request: A sample Request instance.
    """
    return Request(
        wallet_address="T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        created_at=datetime.now(UTC)
    )