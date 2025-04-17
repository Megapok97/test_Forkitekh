from fastapi import FastAPI, Depends, HTTPException, Request
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, tron_service, database
from app.logger import setup_logger
from tronpy.keys import to_base58check_address

logger = setup_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Yields control back to the application during its runtime.

    Notes:
        - Ensures the Tron client and database connections are properly closed when the application shuts down.
    """
    yield
    await tron_service.tron_client.close()
    await database.close_db()


app = FastAPI(title="Tron Wallet Info Service", lifespan=lifespan)


@app.post("/wallet", response_model=schemas.WalletResponse)
async def get_wallet_info(
        request: schemas.WalletRequest,
        db: AsyncSession = Depends(database.get_db),
        client_request: Request = None
):
    """
    Retrieves wallet information for a given Tron address.

    Args:
        request (schemas.WalletRequest): The request containing the Tron wallet address.
        db (AsyncSession): Asynchronous database session for storing the request.
        client_request (Request, optional): FastAPI request object to extract client IP.

    Returns:
        schemas.WalletResponse: Wallet information including balance, bandwidth, and energy.

    Raises:
        HTTPException:
            - 400 if the Tron address is invalid or an error occurs while fetching wallet info.
    """
    client_ip = client_request.client.host if client_request else "unknown"
    logger.info(f"Incoming request: POST /wallet from {client_ip}, address={request.address}")

    try:
        to_base58check_address(request.address)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid Tron address: {str(e)}")

    try:
        wallet_info = await tron_service.get_wallet_info(request.address)
        await crud.create_request(db, request.address)
        logger.info(f"Successfully processed wallet info for address={request.address}")
        return wallet_info
    except ValueError as e:
        logger.error(f"Error processing wallet info for address={request.address}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/requests", response_model=list[schemas.RequestResponse])
async def get_requests(
        params: schemas.PaginationParams = Depends(),
        db: AsyncSession = Depends(database.get_db),
        client_request: Request = None
):
    """
    Retrieves a paginated list of requests stored in the database.

    Args:
        params (schemas.PaginationParams): Pagination parameters (offset and limit).
        db (AsyncSession): Asynchronous database session for querying requests.
        client_request (Request, optional): FastAPI request object to extract client IP.

    Returns:
        list[schemas.RequestResponse]: List of request records.

    Raises:
        HTTPException:
            - 500 if an error occurs while retrieving requests from the database.
    """
    client_ip = client_request.client.host if client_request else "unknown"
    logger.info(f"Incoming request: GET /requests from {client_ip}, offset={params.offset}, limit={params.limit}")

    try:
        requests = await crud.get_requests(db, params.offset, params.limit)
        logger.info(f"Successfully retrieved {len(requests)} requests")
        return requests
    except Exception as e:
        logger.error(f"Error retrieving requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
