from config import API
from typing import List

class BugcrowdAPI(API):
    def __init__(self) -> None:
        """
        Initialize a new BugcrowdAPI object.
        """
        super().__init__(base_url='https://bugcrowd.com')

    async def paginate(self, endpoint: str) -> List[dict]:
        """
        Generator that retrieves all paginated results from the given API endpoint.

        Args:
            endpoint (str): The API endpoint to request.

        Yields:
            dict: A dictionary representing the response JSON for each page.
        """
        params = {'page[]': 1}
        while True:
            response_json = await self.get(endpoint, params=params)
            yield response_json
            if response_json['meta']['totalPages'] > params['page[]'] - 1:
                params['page[]'] += 1
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
        response_json = []

        # Retrieve the target groups for the specified scope.
        target_groups = await self.get(f"{self.base_url}/{scope}/target_groups.json")
        target_groups = target_groups.get("groups", [])

        # Iterate over each target group and retrieve the targets.
        for target_group in target_groups:
            targets = await self.get(f"{self.base_url}{target_group['targets_url']}.json")
            target_group["targets"] = targets.get("targets", [])

            response_json.append(target_group)

        yield {"target_groups": response_json}
