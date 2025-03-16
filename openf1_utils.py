import httpx
from typing import Literal, List, Optional
from f1_types import Session, Driver, Lap, MiniSectorValue, TrackConditions
from loguru import logger

BASE_URL = "https://api.openf1.org/v1"


async def get_response(url: str):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            retries += 1
            if retries == max_retries:
                logger.error(
                    f"Failed after {max_retries} retries while fetching {url[len(BASE_URL):]}: {e}"
                )
                return None
            logger.warning(
                f"Retry {retries}/{max_retries} for {url[len(BASE_URL):]}: {e}"
            )
