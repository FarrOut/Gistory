import json
import datetime
from enum import Enum

import requests
import logging
import pytz
from urllib3.exceptions import NewConnectionError


class Rest(Enum):
    GET = 'get'
    POST = 'post'
    PATCH = 'patch'
    DELETE = 'delete'


class Client:
    # ISO 8601 - YYYY-MM-DDTHH:MM:SSZ
    # E.g "2010-04-14T02:15:15Z"
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    __url_prefix = 'https://api.github.com'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    def __init__(self, access_token: str, ):
        self.token = access_token

    def __put_last_access_timestamp(self):
        # TODO refactor __put_last_access_timestamp and __get_last_access_timestamp to reuse common code

        date_obj = datetime.datetime.now(tz=datetime.timezone.utc)
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

    def __submit_request(self, method: Rest, endpoint: str = 'gists', params: dict = {}, data: dict = {}):

        __url = f'{Client.__url_prefix}/{endpoint}'
        Client.logger.debug(f'Submitting request to {__url}...')

        headers = {
            "X-GitHub-Api-Version": '2022-11-28',
            "Accept": "application/vnd.github+json",
            "Authorization": "token {0}".format(self.token),
            # "Content-Type":"application/json",
            # "Time-Zone": "Europe/Amsterdam",
        }

        try:
            if method is Rest.GET:
                with requests.get(__url,
                                  headers=headers,
                                  params=params,
                                  ) as response:
                    return response
            elif method is Rest.POST:
                with requests.post(__url,
                                   headers=headers,
                                   params=params,
                                   data=data,
                                   ) as response:
                    return response
            elif method is Rest.PATCH:
                with requests.patch(__url,
                                    headers=headers,
                                    params=params,
                                    data=data,
                                    ) as response:
                    return response
            elif method is Rest.DELETE:
                with requests.delete(__url,
                                    headers=headers,
                                    params=params,
                                    data=data,
                                    ) as response:
                    return response                

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

        json_ = self.__submit_request(method=Rest.GET, params=params).json()
        Client.logger.debug(f'list_gist found {len(json_)} items.')
        # self.logger.debug(json.dumps(json_, sort_keys=True, indent=4))

        if len(json_) == 0:
            Client.logger.info('No Gists found to list.')
            return
        else:
            self.__output_gists(json_)
        self.__put_last_access_timestamp()

    def create_gist(self, data: dict = {}) -> int:
        Client.logger.debug('Creating a new Gist')

        

        response = self.__submit_request(method=Rest.POST, data=json.dumps(data))

        match response.status_code:
            case 201:
                Client.logger.info('New Gist created.')
            case 304:
                raise Exception('New Gist Not modified.')
            case 403:
                raise Exception('New Gist forbidden.')
            case 404:
                raise Exception('New Gist resource not found.')
            case 422:
                raise Exception(f'New Gist Validation failed, or the endpoint has been spammed.\n{response.text}')
            case _: 
                raise Exception(f'New Gist not created.\n{response.text}')

        response_json = response.json()
        gist_id = response_json['id']

        return gist_id

    def update_gist(self, gist_id: str):
        Client.logger.debug(f'Updating Gist \'{gist_id}\'')

        date_obj = datetime.datetime.now(tz=datetime.timezone.utc)
        timestamp = date_obj.strftime(Client.time_format)

        data = {"description": "An updated gist description",
                  "files": {"test.txt": {"content": f"Updated at {timestamp}"}}}

        response = self.__submit_request(method=Rest.PATCH, endpoint=f'gists/{gist_id}', data=json.dumps(data))

        match response.status_code:
            case 200:
                Client.logger.info(f'Gist {gist_id} successfully updated.')
            case 404:
                raise Exception(f'Gist {gist_id} resource not found.')
            case 422:
                raise Exception(f'Gist {gist_id} Validation failed, or the endpoint has been spammed.\n{response.text}')
            case _:                
                raise Exception(f'Gist {gist_id} not updated.\n{response.text}')

    def delete_gist(self, gist_id: str):
        Client.logger.debug(f'Deleting Gist \'{gist_id}\'')

        params = {"gist_id": gist_id}

        response = self.__submit_request(method=Rest.DELETE, endpoint=f'gists/{gist_id}', params=params)

        match response.status_code:
            case 204:
                Client.logger.info(f'Gist {gist_id} successfully updated.')
            case 404:
                raise Exception(f'Gist {gist_id} resource not found. Because {response.text}')
            case 422:
                raise Exception(f'Gist {gist_id} Validation failed, or the endpoint has been spammed. Because {response.text}')
            case _:                
                raise Exception(f'Gist {gist_id} not deleted. Because {response.text}')