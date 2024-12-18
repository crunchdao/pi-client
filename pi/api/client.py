import os
import time
import typing
import urllib.parse

import inflection
import requests

from .. import constants
from .errors import *
from .models import *


class Client:

    def __init__(
        self,
        api_key: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
    ):
        if api_key is None:
            api_key = os.environ.get(constants.API_KEY_ENVVAR)

        if base_url is None:
            base_url = os.environ.get(constants.BASE_URL_ENVVAR) or constants.BASE_URL_DEFAULT

        self._base_url = base_url

        self._session = requests.Session()
        self._session.params.update({
            "apiKey": api_key,
        })

    def _format_url(self, path: str):
        return urllib.parse.urljoin(self._base_url, path)

    def _request(self, method: str, path: str, **kwargs):
        params = kwargs.pop("params", [])

        response = self._session.request(method, self._format_url(path), params=params, **kwargs)
        content = response.json()

        if not response.ok:
            raise self._map_error(content)

        return response.json()

    def _map_error(self, content: typing.Dict[str, typing.Any]):
        code = content.pop("code", None)
        message = content.pop("message", None)

        error_class = None
        if code:
            camel = inflection.camelize(code.lower()) + "Error"
            error_class = globals().get(camel)

        if error_class is None:
            return GenericApiError(code, message, **content)

        args = {
            inflection.underscore(key): value
            for key, value in content.items()
        }

        return error_class(message, **args)

    def get_current_user(self) -> CurrentUser:
        content = self._request("GET", "v1/users/@me")

        return CurrentUser.from_dict(content)

    def list_datasources(self) -> typing.List[Datasource]:
        content = self._request(
            "GET",
            f"/v1/datasources"
        )

        return [
            Datasource.from_dict(item)
            for item in content
        ]

    def create_question(
        self,
        prompt: str,
        *,
        datasource_name: typing.Optional[str] = None,
        discord_user_id: typing.Optional[str] = None,
        wait: typing.Union[bool | int] = False,
        refresh_interval=0.5,
    ) -> Question:
        url = "/v1/questions"
        extra_body = {}

        if discord_user_id is not None:
            url = "/v1/discord/questions"
            extra_body = {
                "discordUserId": discord_user_id,
            }

        content = self._request(
            "POST",
            url,
            json={
                "prompt": prompt,
                "datasourceName": datasource_name,
                **extra_body,
            }
        )

        question = Question.from_dict(content)

        if int(wait) > 0:
            if wait is True:
                wait = 10**8  # big number

            while not question.is_completed and wait:
                time.sleep(refresh_interval)
                question = self.get_question(question.id)

                wait -= 1

        return question

    def get_question(
        self,
        question_id: int,
    ) -> Question:
        content = self._request(
            "GET",
            f"/v1/questions/{question_id}"
        )

        return Question.from_dict(content)

    def list_question_timeseries(
        self,
        question_id: int,
    ) -> typing.List[Timeseries]:
        content = self._request(
            "GET",
            f"/v1/questions/{question_id}/timeseries"
        )

        return [
            Timeseries.from_dict(item, infer_missing=True)
            for item in content
        ]
