from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class WalletRequest(BaseModel):
    """
    Pydantic model for validating incoming wallet address requests.

    Attributes:
        address (str): Tron wallet address to query.
    """
    address: str


class WalletResponse(BaseModel):
    """
    Pydantic model for the response containing wallet information.

    Attributes:
        balance_trx (float): Wallet balance in TRX.
        bandwidth (int): Available bandwidth for the wallet.
        energy (int): Available energy for the wallet.
    """
    balance_trx: float
    bandwidth: int
    energy: int


class RequestResponse(BaseModel):
    """
    Pydantic model for the response containing request details.

    Attributes:
        id (int): Unique identifier of the request.
        created_at (datetime): Timestamp when the request was created.
        wallet_address (str): Tron wallet address associated with the request.
    """
    id: int
    created_at: datetime
    wallet_address: str

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """
    Pydantic model for pagination parameters in API requests.

    Attributes:
        offset (int): Number of records to skip (default: 0, must be >= 0).
        limit (int): Maximum number of records to return (default: 10, must be between 1 and 100).
    """
    offset: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of records to return")
