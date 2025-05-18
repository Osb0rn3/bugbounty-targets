import json
from typing import List
import logging
import os
from config import API
from platforms.hackerone import HackerOneAPI
from platforms.bugcrowd import BugcrowdAPI
from platforms.intigriti import IntigritiAPI
from platforms.yeswehack import YesWeHackAPI
import concurrent.futures

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

    def get_hackerone_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the HackerOne API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/v1/hackers/programs?page[size]=100'
        response_json = self.api.paginate(endpoint)

        for response in response_json:
            if 'data' in response:
                self.results.extend(response['data'])
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        for scope in self.results:
            scope_handle = scope.get('attributes').get('handle')
            response_json = self.api.program_info(scope_handle)
            
            if 'relationships' in response_json:
                scope['relationships'] = response_json['relationships']
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        self.save_results('hackerone.json')

        self.results = self.api.brief(self.results)
        self.save_results('brief/hackerone.json')
        return self.results

    def get_bugcrowd_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the BugCrowd API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        categories = {
            'vdp': 'vdp',
            'rdp': 'bug_bounty',
        }

        for category, category_key in categories.items():
            endpoint = f'{self.api.base_url}/engagements.json?category={category_key}'
            for response in self.api.paginate(endpoint):
                for engagement in response.get('engagements', []):
                    engagement['category'] = category
                    self.results.append(engagement)

        self.results = self.api.complement_programs(self.results)
        self.results = [scope for scope in self.results if scope['accessStatus'] == 'open']
        
        local_results = []
        for scope in self.results:
            scope_handle = scope.get('briefUrl', '').strip("/")
            response_json = self.api.program_info(scope_handle)

            if response_json and response_json.get('status') != 'deleted':
                scope['target_groups'] = response_json.get('target_groups')
                scope['status'] = response_json.get('status', scope.get('status'))
                local_results.append(scope)
            else:
                self.logger.error("Error: unexpected response format.")

        self.results = local_results
        self.save_results('bugcrowd.json')

        self.results = self.api.brief(self.results)
        self.save_results('brief/bugcrowd.json')

        return self.results
        
    def get_yeswehack_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the YesWeHack API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/programs'
        response_json = self.api.paginate(endpoint)

        for response in response_json:
            if 'items' in response:
                self.results.extend(response['items'])
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        for scope in self.results:
            scope_handle = scope.get('slug')
            response_json = self.api.program_info(scope_handle)

            if 'scopes' in response_json:
                scope['scopes'] = response_json['scopes']
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        self.save_results('yeswehack.json')

        self.results = self.api.brief(self.results)
        self.save_results('brief/yeswehack.json')
        
        return self.results

    def get_intigriti_programs(self) -> List[dict]:
        """
        Retrieve all public programs from the Intigriti API.

        Returns:
            List[dict]: A list of dictionaries representing public programs.
        """
        endpoint = f'{self.api.base_url}/programs'

        response_json = self.api.paginate(endpoint)
        
        for response in response_json:
            if 'records' in response:
                self.results.extend(response['records'])
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        self.results = [scope for scope in self.results if (scope['confidentialityLevel']['id'] == 4 or scope['confidentialityLevel']['id'] == 3)]

        # Exclude duplicate Intigriti program used for testing purposes
        self.results = [scope for scope in self.results if not (scope['handle'] == 'dummy' and scope['name'] == 'Test Program')]

        local_results = []
        for scope in self.results:
            scope_handle = scope.get('id')
            response_json = self.api.program_info(scope_handle)

            if 'domains' in response_json:
                scope['domains'] = response_json['domains']['content']
                local_results.append(scope)
            elif response_json['status'] == 403:
                continue
            else:
                self.logger.error("Error: unexpected response format.")
                continue

        self.results = local_results
        self.save_results('intigriti.json')
        
        self.results = self.api.brief(self.results)
        self.save_results('brief/intigriti.json')

        return self.results

def main():
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

    # Gather program information from multiple platforms sequentially
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(public_programs_bugcrowd.get_bugcrowd_programs)
        executor.submit(public_programs_hackerone.get_hackerone_programs)
        executor.submit(public_programs_intigriti.get_intigriti_programs)
        executor.submit(public_programs_yeswehack.get_yeswehack_programs)

    logging.info("Programs crawled successfully.")

if __name__ == '__main__':
    main()
