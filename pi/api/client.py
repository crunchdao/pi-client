import os
import time
import typing
import urllib.parse

import inflection
import pandas
import requests

from .. import constants
from .errors import *
from .models import *
from .pagination import *


class Client:

    def __init__(
        self,
        api_key: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        page_size: int = 100,
    ):
        if api_key is None:
            api_key = os.environ.get(constants.API_KEY_ENVVAR)

        if base_url is None:
            base_url = os.environ.get(constants.BASE_URL_ENVVAR) or constants.BASE_URL_DEFAULT

        self._base_url = base_url
        self._page_size = page_size

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
        print(content)
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

    def _paginate(
        self,
        requester: typing.Callable[[PageRequest], requests.Response],
        start_page: int = 0,
        page_size: typing.Optional[int] = None,
    ):
        if not page_size:
            page_size = self._page_size

        page_request = PageRequest(start_page, page_size)
        while True:
            page_response = requester(page_request)

            content = page_response["content"]
            for item in content:
                yield item

            if len(content) != page_response["pageSize"]:
                break

            page_request = page_request.next()

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

    @typing.overload
    def list_questions(
        self,
        *,
        as_dataframe: typing.Literal[False] = False,
    ) -> typing.Iterator[Question]:
        ...

    @typing.overload
    def list_questions(
        self,
        *,
        as_dataframe: typing.Literal[True] = True,
    ) -> pandas.DataFrame:
        ...

    def list_questions(
        self,
        *,
        as_dataframe: bool = False,
        only_successful: typing.Optional[bool] = None,
        user_id: typing.Optional[int] = None,
        tags: typing.Optional[typing.List[str]] = None,
        datasource_name: typing.Optional[str] = None,
        created_after: typing.Optional[datetime.datetime] = None,
        created_before: typing.Optional[datetime.datetime] = None,
        vote_direction: typing.Optional[typing.Literal["ANY", "UP", "DOWN"]] = None,
        sort_by: typing.Optional[typing.Literal["HIGHER_SCORE", "HIGHER_CORRELATION", "HIGHER_REWARDED", "RECENT"]] = None,
        start_page: typing.Optional[int] = 0,
    ) -> typing.Union[typing.Iterator[Question] | pandas.DataFrame]:
        params = {}

        if only_successful is not None:
            params["onlySuccessful"] = only_successful

        if user_id is not None:
            params["userId"] = user_id

        if tags is not None:
            params["tags"] = tags

        if datasource_name is not None:
            params["datasource"] = datasource_name

        if created_after is not None:
            params["createdAfter"] = created_after.isoformat()

        if created_before is not None:
            params["createdBefore"] = created_before.isoformat()

        if vote_direction is not None:
            params["voteDirection"] = vote_direction

        if sort_by is not None:
            params["sortBy"] = sort_by

        paginated = self._paginate(
            lambda page_request: self._request(
                "GET",
                "/v1/questions",
                params={
                    **params,
                    "page": page_request.number,
                    "size": page_request.size,
                },
            ),
            start_page=start_page,
        )

        if as_dataframe:
            return pandas.json_normalize([
                dataclasses.asdict(Question.from_dict(item))
                for item in paginated
            ])
        else:
            def mapper():
                for item in paginated:
                    yield Question.from_dict(item)

            return mapper()

    def get_question(
        self,
        question_id: int,
    ) -> Question:
        content = self._request(
            "GET",
            f"/v1/questions/{question_id}"
        )

        return Question.from_dict(content)

    get_question_by_id = get_question

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
