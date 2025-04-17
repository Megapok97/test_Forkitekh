from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC

Base = declarative_base()


class Request(Base):
    """
    SQLAlchemy model representing a request to the Tron Wallet Info Service.

    Attributes:
        __tablename__ (str): Name of the database table ('requests').
        id (Column): Primary key, unique identifier for the request.
        created_at (Column): Timestamp when the request was created, defaults to current UTC time.
        wallet_address (Column): Tron wallet address associated with the request, indexed for faster queries.
    """
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    wallet_address = Column(String, index=True, nullable=False)
