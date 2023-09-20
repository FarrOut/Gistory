import logging
import argparse

from modules.client.client import Client

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser("gistory")
parser.add_argument("-token", "--access_token", help="GitHub Personal Access Token.", type=str)


def main():
    args = parser.parse_args()

    token = str(args.access_token)

    if token is None:
        logger.warning('No access token received!')
    else:
        logger.info('Access token received.')

    client = Client(access_token=token)

    # try:
    #     new_gist_id = client.create_gist(data = {"description": "Example of a gist", "public": False,
    #               "files": {"test.txt": {"content": "Hello World"}}}    )
    #     logger.info(f'New gist created: {new_gist_id}')
    # except Exception as e:
    #     logger.error(f'Failed to create new gist: {e}')

    # try:
    #     client.delete_gist(gist_id='9daa9918e5f85e9ed44504fae46283c8')
    #     logger.info(f'gist deleted')
    # except Exception as e:
    #     logger.error(f'Failed to delete gist: {e}')

    client.update_gist(gist_id='223e16840a2b8b931e8be0af6d36d39d')
    # client.list_gists()


main()
