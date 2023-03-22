import re
import time

import boto3
import requests

URL_SF_API = "https://platform.cloud.petsafe.net/smart-feed/"
PETSAFE_CLIENT_ID = "18hpp04puqmgf5nc6o474lcp2g"
PETSAFE_REGION = "us-east-1"


class PetSafeClient:
    def __init__(self, email, id_token=None, refresh_token=None, access_token=None, session=None):
        self.id_token = id_token
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.email = email
        self.session = session
        self.username = None
        self.token_expires_time = None
        self.challenge_name = None
        self.client = boto3.client("cognito-idp", region_name=PETSAFE_REGION)

    @property
    def headers(self):
        """
        Creates a dict of headers with JSON content-type and token.

        :return: dictionary of headers

        """
        headers = {"Content-Type": "application/json"}

        if self.id_token is None:
            raise Exception("Not authorized! Have you requested a token?")

        if time.time() >= self.token_expires_time - 10:
            self.refresh_tokens()

        headers["Authorization"] = self.id_token

        return headers

    def request_code(self):
        """
        Requests an email code from PetSafe authentication.

        :return: response from PetSafe

        """
        response = self.client.initiate_auth(
            AuthFlow="CUSTOM_AUTH",
            ClientId=PETSAFE_CLIENT_ID,
            AuthParameters={
                "USERNAME": self.email,
                "AuthFlow": "CUSTOM_CHALLENGE",
            },
        )
        self.challenge_name = response["ChallengeName"]
        self.session = response["Session"]
        self.username = response["ChallengeParameters"]["USERNAME"]
        return response

    def request_tokens_from_code(self, code):
        """
        Requests tokens from PetSafe API using emailed code.

        :param code: email code
        :return: response from PetSafe

        """
        response = self.client.respond_to_auth_challenge(
            ClientId=PETSAFE_CLIENT_ID,
            ChallengeName=self.challenge_name,
            Session=self.session,
            ChallengeResponses={
                "ANSWER": re.sub(r"\D", "", code),
                "USERNAME": self.username,
            },
        )
        self.id_token = response["AuthenticationResult"]["IdToken"]
        self.access_token = response["AuthenticationResult"]["AccessToken"]
        self.refresh_token = response["AuthenticationResult"]["RefreshToken"]
        self.token_expires_time = time.time() + response["AuthenticationResult"]["ExpiresIn"]
        return response

    def refresh_tokens(self):
        """
        Refreshes tokens with PetSafe.

        :return: the response from PetSafe.

        """
        response = self.client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": self.refresh_token},
            ClientId=PETSAFE_CLIENT_ID,
        )

        if "Session" in response:
            self.session = response["Session"]

        self.id_token = response["AuthenticationResult"]["IdToken"]
        self.access_token = response["AuthenticationResult"]["AccessToken"]
        self.refresh_token = response["AuthenticationResult"]["RefreshToken"]
        self.token_expires_time = time.time() + response["AuthenticationResult"]["ExpiresIn"]
        return response

    def api_post(self, path="", data=None):
        """
        Sends a POST to PetSafe SmartFeed API.

        Example: api_post(path=feeder.api_path + 'meals', data=food_data)

        :param path: the path on the API
        :param data: the POST data
        :return: the request response

        """
        return requests.post(URL_SF_API + path, headers=self.headers, json=data)

    def api_get(self, path=""):
        """
        Sends a GET to PetSafe SmartFeed API.

        Example: api_get(path='feeders')

        :param path: the path on the API
        :return: the request response

        """
        return requests.get(URL_SF_API + path, headers=self.headers)

    def api_put(self, path="", data=None):
        """
        Sends a PUT to PetSafe SmartFeed API.

        Example: api_put(path='feeders', data=my_data)

        :param path: the path on the API
        :param data: the PUT data
        :return: the request response

        """
        return requests.put(URL_SF_API + path, headers=self.headers, json=data)

    def api_delete(self, path=""):
        """
        Sends a DELETE to PetSafe SmartFeed API.

        Example: api_delete(path=feeder.api_path + 'schedules')

        :param path: the path on the API
        :return: the request response

        """
        return requests.delete(URL_SF_API + path, headers=self.headers)
