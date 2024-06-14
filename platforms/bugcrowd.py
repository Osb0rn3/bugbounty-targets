from config import API
from typing import List

class BugcrowdAPI(API):
    def __init__(self) -> None:
        """
        Initialize a new BugcrowdAPI object.
        """
        super().__init__(base_url='https://bugcrowd.com')

    def transform_item(self, item, key_mapping, skip_keys):
        """
        Recursively transform keys in the item based on the key_mapping,
        and skip keys in skip_keys.
        """
        if isinstance(item, dict):
            return {
                (key_mapping[k] if k in key_mapping else k): self.transform_item(v, key_mapping, skip_keys)
                for k, v in item.items()
                if k not in skip_keys
            }
        elif isinstance(item, list):
            return [self.transform_item(i, key_mapping, skip_keys) for i in item]
        else:
            return item


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
            if response_json['paginationMeta']['totalCount'] > params['page'] * 24:
                params['page'] += 1
            else:
                break

    async def program_info(self, scope: str) -> dict:
        """
        Retrieves information about the targets in a given scope.

        Args:
            scope (str): The name of the scope to retrieve targets from.

        Returns:
            dict: A dictionary containing the target groups and their respective targets.
        """
        if scope.startswith('engagements/'):
            # Retrieve the change logs for the specified scope.
            changelogs = await self.get(f"{self.base_url}/{scope}/changelog.json")
            changelog_id = changelogs.get("changelogs", [])[0].get('id')

            changelog_data = await self.get(f"{self.base_url}/{scope}/changelog/{changelog_id}.json")
            scope_data = changelog_data.get('data', {}).get('scope', [])

            structured_targets = []
            for item in scope_data:
                skip_keys = {'rewardRange', 'recentChangeFlags'}
                key_mapping = {
                    'inScope': 'in_scope',
                    'sortOrder': 'sort_order',
                    'rewardRangeData': 'reward_range',
                    'descriptionHtml': 'description_html'
                }

                new_item = self.transform_item(item, key_mapping, skip_keys)

                for target in new_item.get('targets', []):
                    if target.get('tags'):
                        target['target'] = {'tags': target.pop('tags')}

                structured_targets.append(new_item)

            yield {"target_groups": structured_targets}

        else:
            # Retrieve the target groups for the specified scope.
            target_groups_response = await self.get(f"{self.base_url}/{scope}/target_groups.json")
            target_groups = target_groups_response.get("groups", [])

            # Retrieve targets for each target group.
            for target_group in target_groups:
                targets_response = await self.get(f"{self.base_url}{target_group['targets_url']}.json")
                target_group["targets"] = targets_response.get("targets", [])

            yield {"target_groups": target_groups}
