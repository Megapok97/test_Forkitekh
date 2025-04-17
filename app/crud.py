from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Request
from datetime import datetime, UTC
from app.logger import setup_logger

logger = setup_logger("crud")


async def create_request(db: AsyncSession, wallet_address: str) -> Request:
    """
    Creates a new request record in the database.

    Args:
        db (AsyncSession): Asynchronous SQLAlchemy session for database operations.
        wallet_address (str): Tron wallet address associated with the request.

    Returns:
        Request: The created request object from the `requests` table.

    Raises:
        Exception: If an error occurs while writing to the database (e.g., connection issues).
    """
    try:
        db_request = Request(wallet_address=wallet_address, created_at=datetime.now(UTC))
        db.add(db_request)
        await db.commit()
        await db.refresh(db_request)
        logger.info(f"Created request in DB: wallet_address={wallet_address}, id={db_request.id}")
        return db_request
    except Exception as e:
        logger.error(f"Failed to create request in DB for wallet_address={wallet_address}: {str(e)}")
        raise


async def get_requests(db: AsyncSession, offset: int, limit: int) -> list[Request]:
    """
    Retrieves a paginated list of recent requests from the database.

    Args:
        db (AsyncSession): Asynchronous SQLAlchemy session for database operations.
        offset (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.

    Returns:
        list[Request]: List of `Request` objects, sorted by creation time (descending).

    Raises:
        Exception: If an error occurs while reading from the database (e.g., connection issues).
    """
    try:
        result = await db.execute(
            select(Request)
            .order_by(Request.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        requests = list(result.scalars().all())
        logger.info(f"Retrieved {len(requests)} requests from DB with offset={offset}, limit={limit}")
        return requests
    except Exception as e:
        logger.error(f"Failed to retrieve requests from DB with offset={offset}, limit={limit}: {str(e)}")
        raise
