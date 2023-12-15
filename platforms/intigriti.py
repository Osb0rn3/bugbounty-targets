from config import API
from typing import List

class IntigritiAPI(API):
    def __init__(self, token: str) -> None:
        """
        Initialize a new BugcrowdAPI object.
        """
        super().__init__(base_url='https://api.intigriti.com/external/researcher/v1')
        self.session.headers = {
            'Authorization': f'Bearer {token}'
        }

    async def paginate(self, endpoint: str, offset: int = 0, limit: int = 500) -> List[dict]:
        """
        Generator that retrieves paginated results from the given API endpoint with offset and limit.

        Args:
            endpoint (str): The API endpoint to request.
            offset (int): The starting offset for pagination.
            limit (int): The number of items to retrieve per page.

        Yields:
            dict: A dictionary representing the response JSON for each page.
        """
        while True:
            params = {
                'offset': offset,
                'limit': limit
            }
            
            response_json = await self.get(endpoint, params=params)
            if response_json['records'] != []:
                offset += limit
                yield response_json
            else:
                break

    async def program_info(self, scope: str) -> dict:
        """
        Retrieves information about the targets in a given scope.

        Args:
            scope (str): The name of the scope to retrieve targets from.

        Returns:
            list: A list of dictionaries representing the targets.
        """
        response_json = await self.get(f"{self.base_url}/programs/{scope}")
        yield response_json
