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

    def paginate(self, endpoint: str) -> List[dict]:
        """
        Retrieve all paginated results from the given API endpoint.

        Args:
            endpoint (str): The API endpoint to request.

        Returns:
            List[dict]: A list of dictionaries representing the response JSON for each page.
        """
        results = []
        params = {
            'page[size]': 100
        }

        while True:
            response_json = self.get(endpoint, params=params)
            results.append(response_json)

            if 'next' in response_json['links']:
                endpoint = response_json['links']['next']
            else:
                break

        return results

    def program_info(self, scope: str) -> dict:
        """
        Gathering information of a scope with the HackerOne API.

        Args:
            scope (str): HackerOne program scope handle.

        Returns:
            dict: A dictionary representing the response JSON for scope information.
        """
        data = []
        for structured_scope in self.paginate(f"{self.base_url}/v1/hackers/programs/{scope}/structured_scopes"):
            if 'data' in structured_scope:
                data.extend(structured_scope['data'])

        return {"relationships": {"structured_scopes": {"data": data}}}

    def brief(self, results: dict) -> dict:
        return [
            {
                "handle": result.get('attributes').get('handle'),
                "bounty": 1 if result.get('attributes').get('offers_bounties') else 0,
                "active": 1 if result.get('attributes').get('submission_state') == 'open' else 0,
                "assets": {
                    "in_scope": [
                        {'identifier': scope.get('attributes').get('asset_identifier'), 'type': scope.get('attributes').get('asset_type')}
                        for scope in result.get('relationships').get('structured_scopes').get('data')
                        if scope.get('attributes').get('eligible_for_submission')
                    ],
                    "out_of_scope": [
                        {'identifier': scope.get('attributes').get('asset_identifier'), 'type': scope.get('attributes').get('asset_type')}
                        for scope in result.get('relationships').get('structured_scopes').get('data')
                        if scope.get('attributes').get('eligible_for_submission') == False
                    ],
                }
            } for result in results
        ]