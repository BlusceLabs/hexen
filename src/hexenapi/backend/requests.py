"""
HTTP session for server interaction.
Self-contained — no imports from hexenapi.v1 or hexenapi.v3.
"""

import json

import httpx
from httpx import Response
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from httpx._types import CookieTypes, HeaderTypes, ProxyTypes, TimeoutTypes

from hexenapi.backend._bases import BaseMovieboxException
from hexenapi.backend.constants import DOWNLOAD_REQUEST_HEADERS
from hexenapi.backend.exceptions import EmptyResponseError, MissingAuthError
from hexenapi.backend.helpers import (
    get_absolute_url,
    process_api_response,
)

# ---------------------------------------------------------------------------
# Simple data models for session state
# ---------------------------------------------------------------------------

request_cookies = {}


class UserInfo:
    """Frozen user-info data class"""

    __slots__ = ("token", "userId", "userType", "appType")

    def __init__(self, token: str, userId: str, userType: int, appType: int):
        self.token = token
        self.userId = userId
        self.userType = userType
        self.appType = appType


class MovieboxAppInfo:
    """App-info data class"""

    __slots__ = ("channelType", "pkgName", "url", "versionCode", "versionName")

    def __init__(self, channelType, pkgName, url, versionCode, versionName):
        self.channelType = channelType
        self.pkgName = pkgName
        self.url = url
        self.versionCode = versionCode
        self.versionName = versionName


# ---------------------------------------------------------------------------
# Session (self-contained, was v1.requests.Session + v2.requests.Session)
# ---------------------------------------------------------------------------

__all__ = ["Session"]


class Session:
    """Performs actual get & post http requests asynchronously
    with or without cookies on demand.
    """

    _moviebox_app_info_url = get_absolute_url(
        "/wefeed-h5-bff/app/get-latest-app-pkgs?app_name=moviebox"
    )
    _user_info_endpoint = (
        "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/search-suggest"
    )

    def __init__(
        self,
        headers: HeaderTypes | None = DOWNLOAD_REQUEST_HEADERS,
        cookies: CookieTypes | None = request_cookies,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        proxy: ProxyTypes | None = None,
        **httpx_kwargs,
    ):
        self._headers = headers
        self._cookies = cookies
        self._timeout = timeout
        self._proxy = proxy
        self._client = httpx.AsyncClient(
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            proxy=proxy,
            **httpx_kwargs,
        )
        self.moviebox_app_info: MovieboxAppInfo | None = None
        self.user_info: UserInfo | None = None
        self.__moviebox_app_info_fetched: bool = False

    def _validate_response(self, response: Response) -> Response:
        if response is None or not bool(response.content):
            raise EmptyResponseError(
                response, "Server returned an empty body response."
            )
        return response

    def __repr__(self):
        return rf"<Session(MovieBoxAPI) timeout={self._timeout}>"

    async def get(
        self, url: str, params: dict | None = None, **kwargs
    ) -> Response:
        async with httpx.AsyncClient(
            headers=self._headers,
            cookies=self._cookies,
            proxy=self._proxy,
            timeout=self._timeout,
            **kwargs,
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return self._validate_response(response)

    async def get_from_api(self, *args, **kwargs) -> dict:
        response = await self.get(*args, **kwargs)
        return process_api_response(response)

    async def get_with_cookies(
        self, url: str, params: dict | None = None, **kwargs
    ) -> Response:
        await self.ensure_cookies_are_assigned()
        response = await self._client.get(url, params=params, **kwargs)
        response.raise_for_status()
        return self._validate_response(response)

    async def get_with_cookies_from_api(self, *args, **kwargs) -> dict:
        response = await self.get_with_cookies(*args, **kwargs)
        return process_api_response(response)

    async def post(self, url: str, json: dict, **kwargs) -> Response:
        await self.ensure_cookies_are_assigned()
        response = await self._client.post(url, json=json, **kwargs)
        response.raise_for_status()
        return self._validate_response(response)

    async def post_to_api(self, *args, **kwargs) -> dict:
        response = await self.post(*args, **kwargs)
        return process_api_response(response)

    async def ensure_cookies_are_assigned(self) -> bool:
        if not self.__moviebox_app_info_fetched:
            await self._fetch_user_info()
            await self._fetch_app_info()
            self.__moviebox_app_info_fetched = True
        return (
            self._client.cookies.get("account") is not None
            and self._client.cookies.get("token") is not None
        )

    async def _fetch_app_info(self) -> MovieboxAppInfo:
        response = await self._client.get(url=self._moviebox_app_info_url)
        response.raise_for_status()
        moviebox_app_info = process_api_response(response)
        if isinstance(moviebox_app_info, list):
            moviebox_app_info = moviebox_app_info[0]
        self.moviebox_app_info = MovieboxAppInfo(**moviebox_app_info)
        return self.moviebox_app_info

    async def _fetch_user_info(self) -> UserInfo:
        response = await self._client.post(
            url=self._user_info_endpoint,
            json={"keyword": "avatar", "perPage": 0},
        )
        response.raise_for_status()
        user_info = response.headers.get("x-user")
        if not user_info:
            raise MissingAuthError(
                "App-info response misses x-user key in headers"
            )
        self.user_info = UserInfo(**json.loads(user_info))
        self._client.headers.update(
            {"Authorization": f"Bearer {self.user_info.token}"}
        )
        return self.user_info

    update_session_cookies = _fetch_app_info
