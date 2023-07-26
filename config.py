import asyncio
import logging
import httpx
import json
from tenacity import (retry, stop_after_attempt, wait_random_exponential, before_log,
                      retry_if_exception_type, after_log)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class API:
    def __init__(self, base_url: str, rate_limit: float = 0.5) -> None:
        self.base_url = base_url
        self.session = httpx.AsyncClient()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rate_limit = rate_limit

    async def _wait(self):
        await asyncio.sleep(self.rate_limit)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception_type(
            (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError)),
        after=after_log(logger, logging.WARNING)
    )
    async def get(self, endpoint: str, params: dict = None) -> dict:
        """
        Send an HTTP GET request to the specified API endpoint and return the response as a dictionary.

        Args:
            endpoint (str): The API endpoint to request.
            params (dict): Query parameters to include in the request.

        Returns:
            dict: A dictionary representing the response JSON.
        """
        try:
            response = await self.session.get(endpoint, params=params, timeout=60.0)
            response.raise_for_status()
            await self._wait()
            return response.json()
        except httpx.RequestError as e:
            self.logger.error(f"Error: {e}, Endpoint: {endpoint}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Error decoding response JSON: {e}, Endpoint: {endpoint}")
            raise
        except Exception as e:
            # Ignore any error raised after all retry attempts
            self.logger.warning(f"Ignoring error after all attempts: {e}")
            return {}
