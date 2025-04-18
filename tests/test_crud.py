import pytest
from app import crud
from app.models import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime


@pytest.mark.anyio
async def test_create_request(async_session: AsyncSession):
    """
    Tests the create_request function in crud.py.

    Args:
        async_session: Async SQLAlchemy session fixture.
    """
    wallet_address = "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb"
    request = await crud.create_request(async_session, wallet_address)

    assert request.wallet_address == wallet_address
    assert isinstance(request.created_at, datetime)
    assert request.id is not None


@pytest.mark.anyio
async def test_get_requests(async_session: AsyncSession, sample_request: Request):
    """
    Tests the get_requests function in crud.py with pagination.

    Args:
        async_session: Async SQLAlchemy session fixture.
        sample_request: Sample Request object fixture.
    """
    async_session.add(sample_request)
    await async_session.commit()

    # Debug: Check database state
    result = await async_session.execute(select(Request))
    requests_in_db = result.scalars().all()
    print(f"Requests in DB before get_requests: {len(requests_in_db)}")

    requests = await crud.get_requests(async_session, offset=0, limit=10)

    assert len(requests) == 1
    assert requests[0].wallet_address == sample_request.wallet_address
