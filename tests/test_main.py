import pytest
from fastapi.testclient import TestClient
from app import schemas
from app.models import Request
from sqlalchemy import select
from unittest.mock import AsyncMock


@pytest.mark.anyio
async def test_get_wallet_info_success(client, mocker):
    """
    Tests the /wallet endpoint with a valid Tron address.

    Args:
        client: FastAPI TestClient fixture.
        mocker: Pytest-mock fixture for mocking dependencies.
    """
    mock_wallet_info = {
        "balance_trx": 100.5,
        "bandwidth": 500,
        "energy": 1000
    }
    mocker.patch("app.tron_service.get_wallet_info", AsyncMock(return_value=mock_wallet_info))

    response = client.post("/wallet", json={"address": "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb"})

    assert response.status_code == 200
    assert response.json() == mock_wallet_info


@pytest.mark.anyio
async def test_get_wallet_info_invalid_address(client):
    """
    Tests the /wallet endpoint with an invalid Tron address.

    Args:
        client: FastAPI TestClient fixture.
    """
    response = client.post("/wallet", json={"address": "invalid_address"})

    assert response.status_code == 400
    assert "Invalid Tron address" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_requests_success(client, async_session, sample_request):
    """
    Tests the /requests endpoint with existing requests in the database.

    Args:
        client: FastAPI TestClient fixture.
        async_session: Async SQLAlchemy session fixture.
        sample_request: Sample Request object fixture.
    """
    async_session.add(sample_request)
    await async_session.commit()

    # Debug: Check database state
    result = await async_session.execute(select(Request))
    requests_in_db = result.scalars().all()
    print(f"Requests in DB before GET /requests: {len(requests_in_db)}")

    response = client.get("/requests?offset=0&limit=10")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["wallet_address"] == sample_request.wallet_address


@pytest.mark.anyio
async def test_get_requests_empty(client, async_session):
    """
    Tests the /requests endpoint with no requests in the database.

    Args:
        client: FastAPI TestClient fixture.
        async_session: Async SQLAlchemy session fixture.
    """
    # Debug: Check database state
    result = await async_session.execute(select(Request))
    requests_in_db = result.scalars().all()
    print(f"Requests in DB before GET /requests (empty): {len(requests_in_db)}")

    response = client.get("/requests?offset=0&limit=10")

    assert response.status_code == 200
    assert response.json() == []