import logging
import argparse

from modules.client.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser("gistory")
parser.add_argument("-token", "--access_token", help="GitHub Personal Access Token.", type=str)


def main():
    args = parser.parse_args()

    token = str(args.access_token)
    client = Client(access_token=token)
    client.list_gists()


main()
