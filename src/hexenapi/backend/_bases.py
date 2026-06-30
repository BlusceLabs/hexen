"""
This module contains base classes for the entire package.
Self-contained — no imports from hexenapi.v1 or hexenapi.v3.
"""

import asyncio
import os
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from throttlebuster import DownloadedFile, ThrottleBuster

from hexenapi.backend._web_models import SpecificItemDetailsModel
from hexenapi.backend.exceptions import (
    BaseMovieboxException,
    InvalidDetailPathError,
)
from hexenapi.backend.helpers import (
    assert_instance,
    get_absolute_url,
    sanitize_item_name,
    validate_detail_path,
)
from hexenapi.utils import get_event_loop

# -------------------------------------------------------------------------
# Constants inlined so v2/_bases is fully self-contained
# -------------------------------------------------------------------------
CURRENT_WORKING_DIR = Path(os.getcwd())
DEFAULT_CHUNK_SIZE: int = 1024 * 1024
DEFAULT_TASKS: int = 5
DOWNLOAD_PART_EXTENSION: str = ".part"
DOWNLOAD_REQUEST_HEADERS = {
    "Accept": "*/*",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 "
        "Firefox/137.0"
    ),
    "Referer": "https://fmoviesunblocked.net/",
}


# =====================================================================
# Classes from v1._bases
# =====================================================================
class BaseContentProvider(ABC):
    """Provides easy retrieval of resource from moviebox"""

    @abstractmethod
    async def get_content(self, *args, **kwargs) -> dict | list[dict]:
        raise NotImplementedError("Function needs to be implemented in subclass.")

    @abstractmethod
    async def get_content_model(self, *args, **kwargs) -> object | list[object]:
        raise NotImplementedError("Function needs to be implemented in subclass.")


class ContentProviderHelper:
    """Provides common methods to content provider classes"""

    def get_content_sync(self, *args, **kwargs) -> dict | list[dict]:
        return get_event_loop().run_until_complete(
            self.get_content(*args, **kwargs)
        )

    def get_content_model_sync(self, *args, **kwargs) -> object | list[object]:
        return get_event_loop().run_until_complete(
            self.get_content_model(*args, **kwargs)
        )


class BaseContentProviderAndHelper(BaseContentProvider, ContentProviderHelper):
    """Combines BaseContentProvider(ABC) and ContentProviderHelper"""


class BaseFileDownloader(ABC):
    """Base class for media and caption files downloader (v1 style)"""

    @abstractmethod
    async def run(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        raise NotImplementedError("Function needs to be implemented in subclass.")


class FileDownloaderHelper:
    """Provide common method to file downloaders (v1 style)"""

    def run_sync(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        return asyncio.get_event_loop().run_until_complete(
            self.run(*args, **kwargs)
        )


class BaseFileDownloaderAndHelper(FileDownloaderHelper, BaseFileDownloader):
    """Inherits both FileDownloaderHelper and BaseFileDownloader (v1 style)"""

    @classmethod
    def create_final_dir(
        cls,
        working_dir: Path,
        search_results_item: object,
        season: int,
        episode: int,
        test: bool,
        group: bool,
    ):
        if group and season and episode:
            working_dir = Path(working_dir)
            assert (
                working_dir.exists()
            ), f"The chosen working directory does not exist - {working_dir}"
            final_dir = working_dir.joinpath(
                f"{search_results_item.title} "
                f"({search_results_item.releaseDate.year})",
                f"S{season}",
            )
            if not test:
                os.makedirs(final_dir, exist_ok=True)
            return final_dir
        return working_dir


# =====================================================================
# Classes from v3._bases (ThrottleBuster-based downloader)
# =====================================================================
class V3BaseFileDownloader(ABC):
    """Base class for media and caption files downloader (v3 style)"""

    @abstractmethod
    async def run(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        raise NotImplementedError("Function needs to be implemented in subclass.")


class V3FileDownloaderHelper:
    """Provide common method to file downloaders (v3 style)"""

    def run_sync(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        return asyncio.get_event_loop().run_until_complete(
            self.run(*args, **kwargs)
        )


class V3FileDownloaderAndHelper(V3FileDownloaderHelper, V3BaseFileDownloader):
    """Inherits both V3FileDownloaderHelper and V3BaseFileDownloader"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}

    def __init__(
        self,
        dir: Path | str = CURRENT_WORKING_DIR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        group_series: bool = False,
        **httpx_kwargs,
    ):
        httpx_kwargs.setdefault("cookies", self.request_cookies)
        self.group_series = group_series
        self.throttle_buster = ThrottleBuster(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            request_headers=self.request_headers,
            **httpx_kwargs,
        )

    @classmethod
    def create_final_dir(
        cls,
        working_dir: Path,
        downloadable_files_detail: object,
        season: int,
        episode: int,
        test: bool,
        group: bool,
    ):
        if group and season and episode:
            working_dir = Path(working_dir)
            assert (
                working_dir.exists()
            ), f"The chosen working directory does not exist - {working_dir}"
            final_dir = working_dir.joinpath(
                f"{downloadable_files_detail.subject_title} "
                f"({downloadable_files_detail.release_date.year})",
                f"S{season}",
            )
            if not test:
                os.makedirs(final_dir, exist_ok=True)
            return final_dir
        return working_dir


# =====================================================================
# v2 BaseItemDetails
# =====================================================================
class BaseItemDetails(BaseContentProviderAndHelper):
    """Base class for specific movie/tv-series (item) details"""

    api_endpoint = get_absolute_url("/wefeed-h5api-bff/detail")

    def __init__(self, session):
        from hexenapi.backend.requests import Session as SessionType

        assert_instance(session, SessionType, "session")
        self._session = session

    def _validate_detail_path(self, detail_path: str) -> None:
        if not validate_detail_path(detail_path):
            raise InvalidDetailPathError(
                f"Invalid detail path passed {detail_path!r} "
                "Recheck and try again"
            )

    async def get_content(self, detail_path: str) -> dict:
        self._validate_detail_path(detail_path)
        content = await self._session.get_from_api(
            self.api_endpoint, params={"detailPath": detail_path}
        )
        current_name = content["subject"]["title"]
        content["subject"]["title"] = sanitize_item_name(current_name)
        return content

    async def get_content_model(
        self, detail_path: str, **kwargs
    ) -> SpecificItemDetailsModel:
        content = await self.get_content(detail_path, **kwargs)
        modelled_content = SpecificItemDetailsModel(**content)
        return modelled_content
