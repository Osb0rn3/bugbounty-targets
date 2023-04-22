from config import API
from typing import List

class YesWeHackAPI(API):
    def __init__(self) -> None:
        """
        Initialize a new BugcrowdAPI object.
        """
        super().__init__(base_url='https://api.yeswehack.com')

    async def paginate(self, endpoint: str) -> List[dict]:
        """
        Generator that retrieves all paginated results from the given API endpoint.

        Args:
            endpoint (str): The API endpoint to request.

        Yields:
            dict: A dictionary representing the response JSON for each page.
        """
        params = {'page': 1}
        while True:
            response_json = await self.get(endpoint, params=params)
            yield response_json
            if response_json['pagination']['nb_pages'] > params['page']:
                params['page'] += 1
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
