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
        endpoint = f'{self.api.base_url}/programs.json'
        async for response_json in self.api.paginate(endpoint):
            if 'programs' in response_json:
                self.results.extend(response_json['programs'])
            else:
                self.logger.error("Error: unexpected response format.")
                return []

        self.results = [
            scope for scope in self.results if scope['invited_status'] == 'open']

        for scope in self.results:
            scope_handle = scope.get('code')

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
        response_json = await self.api.get(endpoint)
        if len(response_json) > 0:
            self.results.extend(response_json)
        else:
            self.logger.error("Error: unexpected response format.")
            return []

        self.results = [scope for scope in self.results if scope['confidentialityLevel']
                        == 4 and scope['tacRequired'] == False]

        for scope in self.results:
            scope_handle = f"{scope.get('companyHandle')}/{scope.get('handle')}"
            async for response_json in self.api.program_info(scope_handle):
                if 'domains' in response_json:
                    scope['domains'] = response_json["domains"][-1]["content"]
                else:
                    self.logger.error("Error: unexpected response format.")
                    return []

        self.save_results('intigriti.json')

        return self.results

async def main():
    # Hackerone API credentials
    try:
        HACKERONE_USERNAME = os.environ['HACKERONE_USERNAME']
        HACKERONE_TOKEN = os.environ['HACKERONE_TOKEN']
    except KeyError:
        raise SystemExit('Please provide the Hackerone username/token.')

    hackerone_api = HackerOneAPI(
        username=HACKERONE_USERNAME, token=HACKERONE_TOKEN)
    public_programs_hackerone = PublicPrograms(api=hackerone_api)

    intigriti_api = IntigritiAPI()
    public_programs_intigriti = PublicPrograms(api=intigriti_api)

    bugcrowd_api = BugcrowdAPI()
    public_programs_bugcrowd = PublicPrograms(api=bugcrowd_api)

    yeswehack_api = YesWeHackAPI()
    public_programs_yeswehack = PublicPrograms(api=yeswehack_api)

    await asyncio.gather(
        public_programs_hackerone.get_hackerone_programs(),
        public_programs_intigriti.get_intigriti_programs(),
        public_programs_bugcrowd.get_bugcrowd_programs(),
        public_programs_yeswehack.get_yeswehack_programs()
    )

    logging.info("Programs crawled successfully.")

if __name__ == '__main__':
    asyncio.run(main())
