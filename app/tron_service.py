from tronpy import AsyncTron
from tronpy.exceptions import AddressNotFound, ApiError
from tronpy.providers import AsyncHTTPProvider
from dotenv import load_dotenv
import os
import asyncio
from app.logger import setup_logger

logger = setup_logger("tron_service")

load_dotenv()

TRON_API_KEY = os.getenv("TRON_API_KEY")

if not TRON_API_KEY:
    raise ValueError("TRON_API_KEY is not configured")
tron_client = AsyncTron(AsyncHTTPProvider(api_key=TRON_API_KEY, timeout=30))


async def get_wallet_info(address: str) -> dict:
    """
    Retrieves wallet information from the Tron network.

    Args:
        address (str): Tron wallet address to query.

    Returns:
        dict: Dictionary containing:
            - balance_trx (float): Wallet balance in TRX.
            - bandwidth (int): Available bandwidth for the wallet.
            - energy (int): Available energy for the wallet.

    Raises:
        ValueError:
            - If the address is invalid.
            - If a network error or timeout occurs while contacting the Tron API.
            - If an unexpected error occurs during the API call.
    """
    try:
        account = await tron_client.get_account(address)
        resources = await tron_client.get_account_resource(address)
        balance = account.get("balance", 0) / 1_000_000
        bandwidth = resources["freeNetLimit"] - resources.get("freeNetUsed", 0) + resources.get("NetLimit",
                                                                                                0) - resources.get(
            "NetUsed", 0)
        energy = resources.get("EnergyLimit", 0) - resources.get("EnergyUsed", 0)

        return {
            "balance_trx": balance,
            "bandwidth": bandwidth,
            "energy": energy
        }
    except AddressNotFound:
        logger.error(f"Invalid address: {address}")
        raise ValueError("Invalid address")
    except ApiError as e:
        logger.error(f"Network error while contacting Tron API for address={address}: {str(e)}")
        raise ValueError(f"Network error while contacting Tron API: {str(e)}")
    except asyncio.TimeoutError:
        logger.error(f"Request to Tron API timed out for address={address}")
        raise ValueError("Request to Tron API timed out")
    except Exception as e:
        logger.error(f"Unexpected error while contacting Tron API for address={address}: {str(e)}")
        raise ValueError(f"Unexpected error while contacting Tron API: {str(e)}")
