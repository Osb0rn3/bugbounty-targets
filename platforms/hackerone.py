from config import API
from typing import List
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

class HackerOneAPI(API):
    def __init__(self, username: str, token: str) -> None:
        """
        Initialize a new HackerOneAPI object with the given API credentials.

        Args:
            username (str): HackerOne API username.
            token (str): HackerOne API token.
        """
        super().__init__(base_url='https://api.hackerone.com')
        self.username = username
        self.token = token
        self.session.auth = (self.username, self.token)

    async def paginate(self, endpoint: str) -> List[dict]:
        """
        Generator that retrieves all paginated results from the given API endpoint.

        Args:
            endpoint (str): The API endpoint to request.

        Yields:
            dict: A dictionary representing the response JSON for each page.
        """
        params = {
            'page[size]': 100
        }

        while True:
            response_json = await self.get(endpoint, params=params)
            yield response_json

            if 'next' in response_json['links']:
                endpoint = response_json['links']['next']
            else:
                break

    async def program_info(self, scope: str) -> dict:
        """
        Gathering information of a scope with hackerone API.

        Args:
            scope (str): HackerOne program scope handle.

        Yields:
            dict: A dictionary representing the response JSON for scope information
        """
        data = []
        async for structured_scope in self.paginate(f"{self.base_url}/v1/hackers/programs/{scope}/structured_scopes"):
            if 'data' in structured_scope:
                data.extend(structured_scope['data'])

        yield {"relationships": {"structured_scopes": {"data" : data}}}
