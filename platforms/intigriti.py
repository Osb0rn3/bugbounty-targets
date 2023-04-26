from config import API

class IntigritiAPI(API):
    def __init__(self) -> None:
        """
        Initialize a new BugcrowdAPI object.
        """
        super().__init__(base_url='https://api.intigriti.com/core/public')

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
