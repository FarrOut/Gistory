import json
import datetime
import requests
import logging

from urllib3.exceptions import NewConnectionError


class Client:

    def __init__(self, access_token: str, ):
        self.token = access_token
        self.__url_prefix = 'https://api.github.com'
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def __put_last_access_timestamp(self):
        # TODO refactor __put_last_access_timestamp and __get_last_access_timestamp to reuse common code

        date_obj = datetime.datetime.now()
        # timestamp = date_obj.strftime("%G-%m-%dT%H:%M:%S%Z")
        # ISO 8601 - YYYY-MM-DDTHH:MM:SSZ

        timestamp = date_obj.isoformat()
        timestamp = "2010-04-14T02:15:15Z"
        timestamp = date_obj.timestamp()


        dictionary = {
            'last_accessed': f'{timestamp}'
        }
        json_object = json.dumps(dictionary, indent=4)

        file_name = "gistory.config.json"
        self.logger.debug(f'Recording current access timestamp of {timestamp} to {file_name}')
        with open(file_name, "w") as outfile:
            outfile.write(json_object)

    def __get_last_access_timestamp(self) -> datetime:

        try:

            file_name = "gistory.config.json"
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)
                last_accessed = json_object['last_accessed']

                self.logger.debug(f'Found last access timestamp of \'{last_accessed}\' in {file_name}')
                timestamp = datetime.date.fromtimestamp(float(last_accessed))

                return timestamp

        except ValueError as err:
            self.logger.error('Failed to parse last access timestamp!', exc_info=err)
        except Exception as err:
            self.logger.error('Failed to retrieve last access timestamp!', exc_info=err)

    def __submit_request(self, endpoint: str, params: dict = {}):
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
                              params=params,
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

        id_ = gist_json["id"]
        created_at = gist_json["created_at"]
        description = gist_json["description"]

        owner = gist_json['owner']
        owner_login = owner['login']

        parsed_gist_ = f'Id: {id_}\n'
        parsed_gist_ = f'{parsed_gist_}Created at:{created_at}\n'
        parsed_gist_ = f'{parsed_gist_}Description:{description}\n'
        parsed_gist_ = f'{parsed_gist_}Owner:{owner_login}\n'

        return parsed_gist_

    def list_gists(self):
        self.logger.debug('Listing all Gists')
        timestamp = self.__get_last_access_timestamp()

        if timestamp is not None:
            self.logger.debug(f'Found previous access timestamp of {timestamp.isoformat()}.')
        else:
            self.logger.info(f'Didn\'t find last access timestamp - presuming this is first-time run..')

        params = {"per_page": 30}

        json_ = self.__submit_request(endpoint='gists', params=params)
        self.logger.debug(f'list_gist found {len(json_)} items.')
        # self.logger.debug(json.dumps(json_, sort_keys=True, indent=4))

        self.__output_gists(json_)
        self.__put_last_access_timestamp()
