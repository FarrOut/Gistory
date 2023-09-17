import json
import datetime
import requests
import logging
import pytz
from urllib3.exceptions import NewConnectionError


class Client:
    # ISO 8601 - YYYY-MM-DDTHH:MM:SSZ
    # E.g "2010-04-14T02:15:15Z"
    time_format = "%Y-%m-%dT%H:%M:%S"

    __url_prefix = 'https://api.github.com'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    def __init__(self, access_token: str, ):
        self.token = access_token


    def __put_last_access_timestamp(self):
        # TODO refactor __put_last_access_timestamp and __get_last_access_timestamp to reuse common code

        date_obj = datetime.datetime.now(tz=pytz.UTC)
        # tz = pytz.timezone('Asia/Kolkata')
        # tz.localize(date_obj)
        timestamp = date_obj.strftime(Client.time_format)

        dictionary = {
            'last_accessed': f'{timestamp}'
        }
        json_object = json.dumps(dictionary, indent=4)

        file_name = "gistory.config.json"
        Client.logger.debug(f'Recording current access timestamp of {timestamp} to {file_name}')
        with open(file_name, "w") as outfile:
            outfile.write(json_object)

    def __get_last_access_timestamp(self) -> datetime:

        try:

            file_name = "gistory.config.json"
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)
                last_accessed = json_object['last_accessed']

                Client.logger.debug(f'Found last access timestamp of \'{last_accessed}\' in {file_name}')
                timestamp = datetime.datetime.strptime(last_accessed, self.time_format)

                return timestamp

        except KeyError as err:
            Client.logger.info('Did not find last access timestamp.')
        except ValueError as err:
            Client.logger.error('Failed to parse last access timestamp!', exc_info=err)
        except Exception as err:
            Client.logger.error('Failed to retrieve last access timestamp!', exc_info=err)

    def __submit_request(self, endpoint: str, params: dict = {}):
        __url = f'{Client.__url_prefix}/{endpoint}'
        Client.logger.debug(f'Submitting request to {__url}...')
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
            Client.logger.error('Request failed to establish connection!', exc_info=connErr)
        except Exception as err:
            Client.logger.error('Request failed!', exc_info=err)

    def __output_gists(self, json_: dict):

        for idx, gist_ in enumerate(json_):
            print(f'Gist #{str(idx)}:\n{self.__parse_gist(gist_)}')

    @staticmethod
    def __parse_gist(gist_json: dict) -> str:

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

    @staticmethod
    def __parse_timestamp(datetime_obj: datetime) -> str:

        timestamp = datetime_obj.strftime(Client.time_format)
        # timestamp = "2010-04-14T02:15:15Z"
        parsed_timestamp = f'{timestamp}'

        return parsed_timestamp

    def list_gists(self):
        Client.logger.debug('Listing all Gists')

        params = {"per_page": 30}

        timestamp = self.__get_last_access_timestamp()

        if timestamp is not None:
            timestamp_formatted = self.__parse_timestamp(timestamp)
            Client.logger.debug(f'Only listing Gists last updated since {timestamp_formatted}.')
            params['since'] = timestamp_formatted
        else:
            Client.logger.info(f'Didn\'t find last access timestamp - presuming this is first-time run..')

        json_ = self.__submit_request(endpoint='gists', params=params)
        Client.logger.debug(f'list_gist found {len(json_)} items.')
        # self.logger.debug(json.dumps(json_, sort_keys=True, indent=4))

        self.__output_gists(json_)
        self.__put_last_access_timestamp()
