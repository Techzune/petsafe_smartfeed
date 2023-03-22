import json
import re
import time

import boto3
import requests

from petsafe_smartfeed.devices import DeviceSmartFeed

URL_SF_API = "https://platform.cloud.petsafe.net/smart-feed/"
PETSAFE_CLIENT_ID = "18hpp04puqmgf5nc6o474lcp2g"
PETSAFE_REGION = "us-east-1"


class PetSafeClient:
    def __init__(
        self,
        email,
        id_token=None,
        refresh_token=None,
        access_token=None,
        session=None,
    ):
        """
        Provides a client to PetSafe API.

        Parameters
        ----------
        email : str
            Email address to authorize with PetSafe
        id_token : str, optional
            Authorization ID token provided by PetSafe
        refresh_token : str, optional
            Authorization refresh token provided by PetSafe
        access_token : str, optional
            Authorization access token provided by PetSafe
        session : str, optional
            Authorization session provided by PetSafe

        """
        self.id_token = id_token
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.email = email
        self.session = session
        self.username = None
        self.token_expires_time = 0
        self.challenge_name = None
        self.client = boto3.client("cognito-idp", region_name=PETSAFE_REGION)

    @property
    def headers(self):
        """
        Client request headers with content-type JSON and authorization token.

        Returns
        -------
        dict

        """
        headers = {"Content-Type": "application/json"}

        if self.id_token is None:
            raise Exception("Not authorized! Have you requested a token?")

        if time.time() >= self.token_expires_time - 10:
            self.refresh_tokens()

        headers["Authorization"] = self.id_token

        return headers

    @property
    def feeders(self):
        """
        All feeders attached to the PetSafe account.

        Returns
        -------
        list of DeviceSmartFeed

        """
        """
        Sends a request to PetSafe's API for all feeders associated with account.

        :return: list of Feeders

        """
        response = self.api_get("feeders")
        response.raise_for_status()
        content = response.content.decode("UTF-8")
        return [
            DeviceSmartFeed(self, feeder_data) for feeder_data in json.loads(content)
        ]

    def request_code(self):
        """
        Requests an email code from PetSafe authentication.

        Returns
        -------
        dict
            Authentication response from PetSafe

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
        Requests authentication tokens from PetSafe using emailed code from
        `request_code`.

        Parameters
        ----------
        code : str
            Code provided by PetSafe via email

        Returns
        -------
        dict
            Authentication response from PetSafe

        """
        response = self.client.respond_to_auth_challenge(
            ClientId=PETSAFE_CLIENT_ID,
            ChallengeName=self.challenge_name,
            Session=self.session,
            ChallengeResponses={
                "ANSWER": re.sub(r"\D", "", code),
                "USERNAME": self.username if self.username is not None else self.email,
            },
        )
        self.id_token = response["AuthenticationResult"]["IdToken"]
        self.access_token = response["AuthenticationResult"]["AccessToken"]
        self.refresh_token = response["AuthenticationResult"]["RefreshToken"]
        self.token_expires_time = (
            time.time() + response["AuthenticationResult"]["ExpiresIn"]
        )
        return response

    def refresh_tokens(self, refresh_token=None):
        """
        Requests new authorization tokens from PetSafe using the client's or a
        provided refresh token.

        Parameters
        ----------
        refresh_token : str, optional
            Authorization refresh token provided by PetSafe

        Returns
        -------
        dict
            Authorization response from PetSafe

        """
        if refresh_token is not None:
            self.refresh_token = refresh_token

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
        self.token_expires_time = (
            time.time() + response["AuthenticationResult"]["ExpiresIn"]
        )
        return response

    def api_post(self, path="", data=None):
        """
        Sends a POST request to PetSafe.

        Parameters
        ----------
        path : str
            URL path on the API (it is prepended by the API URL)
        data
            JSON data to send on the request

        Returns
        -------
        Response
            Response received from PetSafe

        Examples
        --------
        >>> client = PetSafeClient("example@email.com", refresh_token="XXXX")
        >>> feeder = client.feeders[0]
        >>> response = client.api_post(path=feeder.api_path + "meals", data={
        ...     "amount": 1,  # feed 1/8th
        ...     "slow_feed": False
        ... })

        """
        return requests.post(URL_SF_API + path, headers=self.headers, json=data)

    def api_get(self, path=""):
        """
        Sends a GET request to PetSafe.

        Parameters
        ----------
        path : str
            URL path on the API (it is prepended by the API URL)

        Returns
        -------
        Response
            Response received from PetSafe

        Examples
        --------
        >>> client = PetSafeClient("example@email.com", refresh_token="XXXX")
        >>> feeders_raw = client.api_get(path="feeders")

        """
        return requests.get(URL_SF_API + path, headers=self.headers)

    def api_put(self, path="", data=None):
        """
        Sends a PUT request to PetSafe.

        Parameters
        ----------
        path : str
            URL path on the API (it is prepended by the API URL)
        data
            JSON data to send on the request

        Returns
        -------
        Response
            Response received from PetSafe

        Examples
        --------
        >>> client = PetSafeClient("example@email.com", refresh_token="XXXX")
        >>> feeder = client.feeders[0]
        >>> response = client.api_put(
        ...    feeder.api_path + "schedules/1",
        ...    data={
        ...        "time": "16:35",  # time in 24 hour format
        ...        "amount": 1,
        ...    },
        ...)

        """
        return requests.put(URL_SF_API + path, headers=self.headers, json=data)

    def api_delete(self, path=""):
        """
        Sends a DELETE request to PetSafe.

        Parameters
        ----------
        path : str
            URL path on the API (it is prepended by the API URL)

        Returns
        -------
        Response
            Response received from PetSafe

        Examples
        --------
        >>> client = PetSafeClient("example@email.com", refresh_token="XXXX")
        >>> feeder = client.feeders[0]
        >>> response = client.api_delete(feeder.api_path + "schedules/1")

        """
        return requests.delete(URL_SF_API + path, headers=self.headers)
