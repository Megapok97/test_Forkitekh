from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Any
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured in environment variables")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Provides an asynchronous database session for dependency injection.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.

    Raises:
        RuntimeError: If the database session cannot be created.
    """
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        raise RuntimeError(f"Failed to create database session: {str(e)}")


async def close_db() -> None:
    """
    Closes the database engine and disposes of all connections.

    Notes:
        - Called during application shutdown to ensure proper resource cleanup.
    """
    await engine.dispose()
