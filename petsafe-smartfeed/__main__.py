import sys
import argparse

from requests import HTTPError

from api import request_token_from_code, request_code
from devices import get_feeders


def cli_feeder(token):
    """
    CLI driven feeder request.

    :param token: the access token for the account
    :return: list of Feeders

    """
    try:
        feeders = get_feeders(token)
    except HTTPError:
        feeders = get_feeders(cli_get_token())
    return feeders


def cli_get_token():
    """
    CLI driven token request. Outputs the token to token.txt.

    :return: the token

    """
    print('Authorization for PetSafe Smart Feed API')
    print()

    # request an email code
    user_email = input('Your email address: ')
    request_code(user_email)

    # request the token
    print('\nPlease check your email for a code from PetSafe.')
    user_code = input('PetSafe email code: ')
    token = request_token_from_code(user_email, user_code)

    # output the token
    print('Your token is:', token)

    # output token to file
    with open('../token.txt', 'w') as f:
        f.write(token)
    print('Saved token to token.txt')
    return token


def load_token_file(file):
    with open(file, 'r') as f:
        return f.read()


parser = argparse.ArgumentParser()

parser.add_argument('-t', '--token',
                    action='store_true',
                    help='generate an access token')

# if no arguments specified, show help
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

# parse for arguments
args = parser.parse_args()

# generate token
if args.token:
    cli_get_token()
    exit(0)
