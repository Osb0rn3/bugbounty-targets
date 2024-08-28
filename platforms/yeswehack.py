from config import API
from typing import List

class YesWeHackAPI(API):
    def __init__(self) -> None:
        """
        Initialize a new YesWeHackAPI object.
        """
        super().__init__(base_url='https://api.yeswehack.com')
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

    def paginate(self, endpoint: str) -> List[dict]:
        """
        Retrieve all paginated results from the given API endpoint.

        Args:
            endpoint (str): The API endpoint to request.

        Returns:
            List[dict]: A list of dictionaries representing the response JSON for each page.
        """
        results = []
        params = {'page': 1}
        while True:
            response_json = self.get(endpoint, params=params)
            results.append(response_json)
            if response_json['pagination']['nb_pages'] > params['page']:
                params['page'] += 1
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

    def brief(self, results: dict) -> dict:
        return [
            {
                "handle": result.get('slug', 'unknown'),
                "bounty": 1 if result.get('bounty', False) else 0,
                "active": 0 if result.get('disabled', False) else 1,
                "assets": {
                    "in_scope": [
                        {
                            'identifier': scope.get('scope', 'unknown'),
                            'type': scope.get('scope_type', 'unknown')
                        }
                        for scope in result.get('scopes', [])
                    ],
                    "out_of_scope": [],
                }
            } for result in results if isinstance(result, dict)
        ]
