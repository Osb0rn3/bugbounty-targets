from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging
import httpx
import json


class API:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session = httpx.AsyncClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError)))
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
            return response.json()
        except httpx.RequestError as e:
            self.logger.error(f"Error: {e}, Endpoint: {endpoint}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Error decoding response JSON: {e}, Endpoint: {endpoint}")
            raise
