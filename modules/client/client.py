import json

import requests
import logging

from urllib3.exceptions import NewConnectionError


class Client:

    def __init__(self, access_token: str, ):
        self.token = access_token
        self.__url_prefix = 'https://api.github.com'
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def __submit_request(self, endpoint: str, results_per_page: int = 30):
        __url = f'{self.__url_prefix}/{endpoint}'
        self.logger.debug(f'Submitting request to {__url}...')
        print(f'Submitting request to {__url}...')  # TODO deleteme

        try:
            with requests.get(__url,
                              headers={
                                  "X-GitHub-Api-Version": '2022-11-28',
                                  "Accept": "application/vnd.github+json",
                                  "Authorization": "token {0}".format(self.token),
                              },
                              params={"per_page": results_per_page},
                              ) as response:
                return response.json()

        except (ConnectionError, requests.exceptions.ConnectionError, NewConnectionError) as connErr:
            self.logger.error('Request failed to establish connection!', exc_info=connErr)
        except Exception as err:
            self.logger.error('Request failed!', exc_info=err)

    def __output_gists(self, json_: dict):

        for idx, gist_ in enumerate(json_):
            print(f'Gist #{str(idx)}:\n{self.__parse_gist(gist_)}')

    def __parse_gist(self, gist_json: dict) -> str:
        # self.logger.debug(f'output_gist given {len(gist_json)} items.')

        id_ = gist_json["id"]
        created_at = gist_json["created_at"]
        description = gist_json["description"]

        owner = gist_json['owner']
        owner_login = owner['login']

        parsed_gist_ = f'Id: {id_}\n'
        parsed_gist_ = f'{parsed_gist_}Created at:{created_at}\n'
        parsed_gist_ = f'{parsed_gist_}Description:{description}\n'
        parsed_gist_ = f'{parsed_gist_}Owner:{owner_login}\n'

        # parsed_gist_.join((f'Created at: {}\n',
        #                   f'Description: {gist_json["description"]}\n'))

        return parsed_gist_

    def list_gists(self):
        self.logger.debug('Listing all Gists')
        json_ = self.__submit_request(endpoint='gists')
        self.logger.debug(f'list_gist found {len(json_)} items.')
        # self.logger.debug(json.dumps(json_, sort_keys=True, indent=4))

        self.__output_gists(json_)
