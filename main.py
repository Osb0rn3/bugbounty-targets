import json
from typing import List
import logging
import os
import asyncio
from config import API
from platforms.hackerone import HackerOneAPI
from platforms.bugcrowd import BugcrowdAPI
from platforms.intigriti import IntigritiAPI
from platforms.yeswehack import YesWeHackAPI


class PublicPrograms:
    """A class to retrieve public programs from Platforms."""

    def __init__(self, api: API) -> None:
        """
        Initialize a new PublicPrograms object with the given API object.

        Args:
            api (API): An API object used to send requests to the API.
        """
        self.api = api
        self.results_directory = './programs'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results: List[dict] = []

    def save_results(self, file_name: str) -> None:
        """
        Save the results in JSON format to the specified file.

        Args:
            file_path (str): The path to the file where the results will be saved.
        """
        if not os.path.exists(self.results_directory):
            os.makedirs(self.results_directory)
        with open(f"{self.results_directory}/{file_name}", 'w') as outfile:
            json.dump(self.results, outfile, indent=4)

    async def get_hackerone_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the HackerOne API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/v1/hackers/programs'

        async for response_json in self.api.paginate(endpoint):
            if 'data' in response_json:
                self.results.extend(response_json['data'])
            else:
                self.logger.error("Error: unexpected response format.")
                return []

        for scope in self.results:
            scope_handle = scope.get('attributes').get('handle')
            async for response_json in self.api.program_info(scope_handle):
                if 'relationships' in response_json:
                    scope['relationships'] = response_json['relationships']
                else:
                    self.logger.error("Error: unexpected response format.")
                    return []

        self.save_results('hackerone.json')

        return self.results

    async def get_bugcrowd_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the BugCrowd API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/engagements.json'
        async for response_json in self.api.paginate(endpoint):
            if 'engagements' in response_json:
                self.results.extend(response_json['engagements'])
            else:
                self.logger.error("Error: unexpected response format.")
                return []

        self.results = [
            scope for scope in self.results if scope['accessStatus'] == 'open']

        for scope in self.results:
            scope_handle = scope.get('briefUrl').split("/")[-1]
            # scope_handle = scope.get('briefUrl').replace("/", "")

            async for response_json in self.api.program_info(scope_handle):
                if 'target_groups' in response_json:
                    scope['target_groups'] = response_json['target_groups']
                else:
                    self.logger.error("Error: unexpected response format.")
                    return []

        self.save_results('bugcrowd.json')

        return self.results

    async def get_yeswehack_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the YesWeHack API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/programs'
        async for response_json in self.api.paginate(endpoint):
            if 'items' in response_json:
                self.results.extend(response_json['items'])
            else:
                self.logger.error("Error: unexpected response format.")
                return []

        for scope in self.results:
            scope_handle = scope.get('slug')
            async for response_json in self.api.program_info(scope_handle):
                if 'scopes' in response_json:
                    scope['scopes'] = response_json['scopes']
                else:
                    self.logger.error("Error: unexpected response format.")
                    return []

        self.save_results('yeswehack.json')

        return self.results

    async def get_intigriti_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the Intigriti API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/programs'

        async for response_json in self.api.paginate(endpoint):
            if 'records' in response_json:
                self.results.extend(response_json['records'])
            else:
                self.logger.error("Error: unexpected response format.")
                return []

        self.results = [scope for scope in self.results if (scope['confidentialityLevel']['id'] == 4 or scope['confidentialityLevel']['id'] == 3)]

        # Exclude duplicate Intigriti program used for testing purposes
        self.results = [scope for scope in self.results if not (scope['handle'] == 'dummy' and scope['name'] == 'Test Program')]

        for scope in self.results:
            scope_handle = scope.get('id')
            async for response_json in self.api.program_info(scope_handle):
                if 'domains' in response_json:
                    scope['domains'] = response_json['domains']['content']
                elif response_json['status'] == 403:
                    self.results.remove(scope)
                else:
                    self.logger.error("Error: unexpected response format.")
                    return []

        self.save_results('intigriti.json')

        return self.results

async def main():
    # Retrieve API credentials from environment variables
    hackerone_username = os.environ.get('HACKERONE_USERNAME')
    hackerone_token = os.environ.get('HACKERONE_TOKEN')
    intigriti_token = os.environ.get('INTIGRITI_TOKEN')

    # Validate and exit if credentials are missing
    if not all([hackerone_username, hackerone_token, intigriti_token]):
        raise SystemExit('Please provide the required API credentials.')

    # Initialize API instances
    hackerone_api = HackerOneAPI(username=hackerone_username, token=hackerone_token)
    intigriti_api = IntigritiAPI(intigriti_token)
    bugcrowd_api  = BugcrowdAPI()
    yeswehack_api = YesWeHackAPI()

    # Initialize PublicPrograms instances for each platform
    public_programs_hackerone = PublicPrograms(api=hackerone_api)
    public_programs_intigriti = PublicPrograms(api=intigriti_api)
    public_programs_bugcrowd  = PublicPrograms(api=bugcrowd_api)
    public_programs_yeswehack = PublicPrograms(api=yeswehack_api)

    # Gather program information from multiple platforms concurrently
    await asyncio.gather(
        public_programs_hackerone.get_hackerone_programs(),
        public_programs_intigriti.get_intigriti_programs(),
        public_programs_bugcrowd.get_bugcrowd_programs(),
        public_programs_yeswehack.get_yeswehack_programs()
    )

    logging.info("Programs crawled successfully.")

if __name__ == '__main__':
    asyncio.run(main())
