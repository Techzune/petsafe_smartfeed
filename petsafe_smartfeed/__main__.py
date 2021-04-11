import sys
import argparse

from . import api


def cli_get_code():
    """
    CLI driven email code request.

    """
    api.request_code(args.email)
    print('Login code requested. Please check your email.')
    print('To generate a login token, run: python -m petsafe_smartfeed', args.email, '-t email_code')


def cli_get_token():
    """
    CLI driven token request.

    :return:  login token

    """
    token = api.request_token_from_code(args.email, args.token)
    print(token)
    return token


# create parser for arguments
parser = argparse.ArgumentParser(usage='python -m petsafe_smartfeed email [-t email_code]')
parser.add_argument('email', help='account email address')
parser.add_argument('-t', '--token', help='generates token from email code')

# if no arguments specified, show help
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

# parse for arguments
args = parser.parse_args()

if args.email and not args.token:
    cli_get_code()
    exit(0)
elif args.email and args.token:
    cli_get_token()
    exit(0)
