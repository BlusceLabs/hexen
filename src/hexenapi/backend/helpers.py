"""
This module provide functions for performing common and frequently required tasks
across the package.
"""

import logging
import re
import typing as t
from dataclasses import dataclass
from math import ceil, floor
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import httpx

from hexenapi.backend.constants import (
    DEFAULT_DUB_LANGUAGE_NAME_OR_CODE,
    HOST_URL,
    ITEM_DETAILS_PATH,
    SEARCH_PER_PAGE_LIMIT,
    VALID_SUBJECT_ID_PATTERN,
)
from hexenapi.backend.exceptions import MissingDubError, UnsuccessfulResponseError
from hexenapi.backend.models.details import (
    DubModel,
    RootItemDetailsModel,
    SeasonItemModel,
)
from hexenapi.utils import get_event_loop

logger = logging.getLogger(__name__)

FILE_EXT_PATTERN = re.compile(r".+\.(\w+)\?.+")

ILLEGAL_CHARACTERS_PATTERN = re.compile(r"[^\w\-_\.\s()&|]")

VALID_ITEM_PAGE_URL_PATTERN = re.compile(
    r"^.*" + ITEM_DETAILS_PATH + r"/[\w-]+(?:\?id\=\d{17,}.*)?$"
)

SCHEME_HOST_PATTERN = re.compile(r"^https?://[-_\.\w]+$")

SERIES_NAME_WITH_SEASON_NUMBER_PATTERN = re.compile(r"^.*\sS\d{1,}$")

SERIES_NAME_WITH_SEASON_NUMBER_ONE_PATTERN = re.compile(r"^.*\sS1$")

UNWANTED_ITEM_NAME_PATTERN = re.compile(r"(\sS\d{1,}|\sS\d{1,}-S\d{1,}|-S\d{1,})")


def get_absolute_url(relative_url: str, base_url: str = HOST_URL) -> str:
    """Makes absolute url from relative one

    Args:
        relative_url (str): Path of a url

    Returns:
        str: Complete url with host
    """

    return urljoin(base_url, SCHEME_HOST_PATTERN.sub("", relative_url))


def assert_membership(value: t.Any, elements: t.Iterable, identity="Value"):
    """Asserts value is a member of elements

    Args:
        value (t.Any): member to be checked against.
        elements (t.Iterable): Iterables of members.
        identity (str, optional): Defaults to "Value".
    """
    assert value in elements, f"{identity} '{value}' is not one of {elements}"


def assert_instance(
    obj: object, class_or_tuple, name: str = "Parameter"
) -> None:
    """assert obj an instance of class_or_tuple"""

    assert isinstance(obj, class_or_tuple), (
        f"{name} value needs to be an instance of/any of {class_or_tuple} "
        f"not {type(obj)}"
    )


def process_api_response(response: httpx.Response) -> dict | list:
    """Extracts the response data field

    Args:
        response (t.Dict): Server response

    Returns:
        t.Dict: Extracted data field value
    """
    expected_content_type = "application/json"
    content_type = response.headers.get("content-type", "")

    if content_type != expected_content_type:
        raise RuntimeError(
            f"Unexpect content type {content_type!r} encountered. "
            f"Expected {expected_content_type!r} - BODY {response.text!r}"
        )

    j: dict = response.json()

    if j.get("code", 1) == 0 and j.get("message") == "ok":
        return j["data"]

    error_msg = (
        "Unsuccessful response received from server -"
        f"STATUS {response.status_code} - BODY: {response.text!r}"
    )

    logger.debug(error_msg)

    raise UnsuccessfulResponseError(
        response,
        error_msg,
    )


extract_data_field_value = process_api_response


def get_file_extension(url: str) -> str | None:
    """Extracts extension from file url e.g `mp4` or `srt`

    For example:
        url : https://valiw.hakunaymatata.com/resource/537977caa8c137031
        85d26471ce7de9f.mp4?auth_key=1753024153-0-0-c824d3b5a5c8acc294bfd41de43c51ef"
        returns 'mp4'
    """
    ext_match = FILE_EXT_PATTERN.match(str(url))

    if ext_match:
        return ext_match.groups()[0]


def validate_item_page_url(url: str) -> str:
    """Checks whether specific item page url is valid"""
    if VALID_ITEM_PAGE_URL_PATTERN.match(url):
        return url

    raise ValueError(f"Invalid url for a specific item page - '{url}'")


def is_valid_search_item(item_name: str) -> bool:
    if SERIES_NAME_WITH_SEASON_NUMBER_PATTERN.match(item_name):
        if SERIES_NAME_WITH_SEASON_NUMBER_ONE_PATTERN.match(item_name):
            return True

        return False

    return True


def sanitize_item_name(item_name: str) -> str:
    return UNWANTED_ITEM_NAME_PATTERN.sub("", item_name)


# ---------------------------------------------------------------------------
# v3-specific helpers (moved from hexenapi.v3.helpers)
# ---------------------------------------------------------------------------


def combine_url_path_with_params(path: str, params: dict):
    parsed = urlparse(path)

    existing_params = dict(parse_qsl(parsed.query))

    merged_params = {**existing_params, **params}
    new_query = urlencode(merged_params)

    return urlunparse(parsed._replace(query=new_query))


def validate_subject_id(subject_id: str) -> bool:
    return VALID_SUBJECT_ID_PATTERN.match(subject_id) is not None


def validate_per_page_and_raise(per_page: int) -> None:
    assert (
        0 < per_page <= SEARCH_PER_PAGE_LIMIT
    ), f"per_page value {per_page} is NOT between 0 and {SEARCH_PER_PAGE_LIMIT}"


def validate_genre_top_id(value: str) -> bool:
    return bool(value)


def validate_detail_path(value: str) -> bool:
    return bool(value)


@dataclass
class RequestParams:
    offset: int
    page: int
    per_page: int
    limit: int


@dataclass
class PaginationDetails:
    total_episodes: int
    request_params: list[RequestParams]


def get_episodes_amount(seasons: list[SeasonItemModel]) -> int:
    return sum(season.total_episodes for season in seasons)


def get_download_tv_series_request_params(
    seasons: list[SeasonItemModel],
    episode: int = 1,
    season: int = 1,
    per_page: int = 20,
    limit: int = -1,
) -> PaginationDetails:
    params: list[RequestParams] = []

    season_numbers = [s.season_number for s in seasons]

    if season not in season_numbers:
        raise ValueError(
            f"Season {season} does not exist. Available seasons: {season_numbers}"
        )

    target_season = next(s for s in seasons if s.season_number == season)
    if episode > target_season.total_episodes:
        raise ValueError(
            f"Episode {episode} exceeds season {season} "
            f"total episodes ({target_season.total_episodes})."
        )

    total_episodes = get_episodes_amount(seasons)
    seasons_before = [s for s in seasons if s.season_number < season]
    offset_episodes = get_episodes_amount(seasons_before) + (episode - 1)
    available_episodes = total_episodes - offset_episodes

    if limit != -1 and limit > available_episodes:
        raise ValueError(
            f"Limit {limit} exceeds available episodes ({available_episodes}) "
            f"from season {season}, episode {episode}."
        )

    no_offset = episode == 1 and season == season_numbers[0]
    no_limit = limit == -1

    if no_offset and no_limit:
        number_of_pages = ceil(total_episodes / per_page)
        for x in range(number_of_pages):
            page_number = x + 1
            loaded_episodes = per_page * x
            page_limit = min(per_page, total_episodes - loaded_episodes)
            params.append(
                RequestParams(
                    offset=0,
                    page=page_number,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
    else:
        wanted_episodes = available_episodes if no_limit else limit

        offset_page = floor(offset_episodes / per_page)
        offset_in_page = offset_episodes % per_page

        loaded = 0

        if offset_in_page > 0:
            page_limit = min(per_page - offset_in_page, wanted_episodes)
            params.append(
                RequestParams(
                    offset=offset_in_page,
                    page=offset_page + 1,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
            loaded += page_limit

        while loaded < wanted_episodes:
            remaining = wanted_episodes - loaded
            current_page = (
                offset_page
                + ceil((loaded + 1) / per_page)
                + (1 if offset_in_page > 0 else 0)
            )
            page_limit = min(per_page, remaining)
            params.append(
                RequestParams(
                    offset=0,
                    page=current_page,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
            loaded += page_limit

        total_episodes = wanted_episodes

    return PaginationDetails(total_episodes=total_episodes, request_params=params)


def get_dub_or_raise(
    item_details: RootItemDetailsModel,
    language_name_or_code: str = DEFAULT_DUB_LANGUAGE_NAME_OR_CODE,
) -> DubModel:

    lan_names = []
    lan_codes = []

    for dub in item_details.dubs:
        if (
            dub.lan_name == language_name_or_code
            or dub.lan_code == language_name_or_code
        ):
            return dub
        else:
            lan_names.append(dub.lan_name)
            lan_codes.append(dub.lan_code)

    raise MissingDubError(
        f"No dub matched that language name or language code "
        f"{language_name_or_code!r}. Availables ones include - "
        f"language_names : {lan_names}, language_codes : {lan_codes}"
    )
