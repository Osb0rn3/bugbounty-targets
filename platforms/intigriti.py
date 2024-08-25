from config import API
from typing import List

class IntigritiAPI(API):
    def __init__(self, token: str) -> None:
        """
        Initialize a new IntigritiAPI object.
        """
        super().__init__(base_url='https://api.intigriti.com/external/researcher/v1')
        self.session.headers = {
            'Authorization': f'Bearer {token}'
        }

    def paginate(self, endpoint: str, offset: int = 0, limit: int = 500) -> List[dict]:
        """
        Retrieve paginated results from the given API endpoint with offset and limit.

        Args:
            endpoint (str): The API endpoint to request.
            offset (int): The starting offset for pagination.
            limit (int): The number of items to retrieve per page.

        Returns:
            List[dict]: A list of dictionaries representing the response JSON for each page.
        """
        results = []
        while True:
            params = {
                'offset': offset,
                'limit': limit
            }
            
            response_json = self.get(endpoint, params=params)
            if response_json['records']:
                results.append(response_json)
                offset += limit
            else:
                break

        return results

    def program_info(self, scope: str) -> dict:
        """
        Retrieves information about the targets in a given scope.

        Args:
            scope (str): The name of the scope to retrieve targets from.

        Returns:
            dict: A dictionary representing the targets.
        """
        response_json = self.get(f"{self.base_url}/programs/{scope}")
        return response_json
