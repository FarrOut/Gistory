import requests
import logging

from urllib3.exceptions import NewConnectionError


class Client:

    def __init__(self, access_token: str, ):
        self.token = access_token
        self.__url_prefix = 'https://api.github.com'
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def __submit_request(self, endpoint: str):
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
                              params={"per_page": 1},
                              ) as response:
                print(response.json())  # TODO deleteme

        except (ConnectionError, requests.exceptions.ConnectionError, NewConnectionError) as connErr:
            self.logger.error('Request failed to establish connection!', exc_info=connErr)
        except Exception as err:
            self.logger.error('Request failed!', exc_info=err)

    def list_gists(self):
        self.logger.debug('Listing all Gists')
        self.__submit_request(endpoint='gists')
