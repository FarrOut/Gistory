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
    client.list_gists()


main()
