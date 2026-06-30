from collections.abc import AsyncIterator
from typing import Any

from hexenapi.backend._bases import V3BaseFileDownloader
from hexenapi.backend.constants import (
    RESULTS_PER_PAGE_AMOUNT,
    CustomResolutionType,
    ResolutionType,
    SubjectType,
    TabID,
)
from hexenapi.backend.exceptions import (
    ExhaustedSearchResultsError,
    ResultsNavigationError,
    ZeroSearchResultsError,
)
from hexenapi.backend.helpers import (
    assert_instance,
    is_valid_search_item,
    sanitize_item_name,
    validate_per_page_and_raise,
    validate_subject_id,
)
from hexenapi.backend.http_client import MovieBoxHttpClient
from hexenapi.backend.models.details import RootItemDetailsModel, SeasonsModel
from hexenapi.backend.models.downloadables import (
    RootCaptionFileMetadata,
    RootDownloadableFilesDetailModel,
    VideoFileMetadata,
)
from hexenapi.backend.models.homepage import RootHomepageModel
from hexenapi.backend.models.search import (
    RootSearchResultsModel,
    RootSearchResultsModelV2,
)
from hexenapi.backend.urls import (
    EXT_CAPTIONS_PATH,
    MAIN_PAGE_PATH,
    RESOURCE_PATH,
    SEARCH_PATH,
    SEARCH_PATH_V2,
    SEASON_INFO_PATH,
    SUBJECT_GET_PATH,
)


class Homepage:
    """Fetches landing page contents"""

    _path = MAIN_PAGE_PATH

    def __init__(self, client_session: MovieBoxHttpClient):
        """Constructor for `Homepage`"""
        self.client_session = client_session
        self._page_number: int = 1
        self._tab_id: int | TabID = 0
        self._version: str = ""

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_tab_id":
                assert_instance(value, (TabID, int), "tab_id")

            case _:
                pass

        super().__setattr__(name, value)

    def _create_params(self) -> dict:
        return {
            "page": self._page_number,
            "tabId": self._tab_id,
            "version": self._version,
        }

    async def get_content(self) -> dict:
        payload = self._create_params()
        contents = await self.client_session.get_from_api(
            self._path, params=payload
        )
        return contents

    async def get_content_model(self, *args, **kwargs) -> RootHomepageModel:
        content = await self.get_content(*args, **kwargs)
        return RootHomepageModel.model_validate(content)

    def get_content_sync(self, *args, **kwargs) -> dict:
        import asyncio

        return asyncio.get_event_loop().run_until_complete(
            self.get_content(*args, **kwargs)
        )

    def get_content_model_sync(self, *args, **kwargs) -> RootHomepageModel:
        import asyncio

        return asyncio.get_event_loop().run_until_complete(
            self.get_content_model(*args, **kwargs)
        )


class Search:
    """Performs a search of movies, tv series, music  etc or both"""

    _path = SEARCH_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
    ):

        self.client_session = client_session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_subject_type":
                assert_instance(value, SubjectType, "_subject_type")

            case _:
                pass

        super().__setattr__(name, value)

    def _create_payload(self) -> dict[str, str | int]:
        return {
            "keyword": self._query,
            "page": self._page,
            "perPage": self._per_page,
            "subjectType": self._subject_type.value,
        }

    async def get_content(self) -> dict:
        contents = await self.client_session.post_to_api(
            self._path, json=self._create_payload()
        )

        if self._subject_type is not SubjectType.ALL:
            target_items = []

            for item in contents["items"]:
                if item["subjectType"] == self._subject_type.value:
                    item_name = item["title"]

                    if is_valid_search_item(item_name):
                        item["title"] = sanitize_item_name(item_name)
                        target_items.append(item)

            contents["items"] = target_items

            if not target_items:
                raise ZeroSearchResultsError(
                    "Search yielded empty results. Try a different keyword."
                )

        return contents

    async def get_content_model(self) -> RootSearchResultsModel:
        contents = await self.get_content()
        return RootSearchResultsModel.model_validate(contents)

    def next_page(self, content: RootSearchResultsModel) -> "Search":
        assert_instance(content, RootSearchResultsModel, "content")

        if content.pager.has_more:
            return Search(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                page=content.pager.next_page,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: RootSearchResultsModel) -> "Search":
        assert_instance(content, RootSearchResultsModel, "content")

        if content.pager.page >= 2:
            return Search(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self,
    ) -> AsyncIterator[RootSearchResultsModel]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model()

            yield content_model

            if content_model.pager.has_more:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False


class SearchV2:
    """Performs a search of movies, tv series, music  etc or both"""

    _path = SEARCH_PATH_V2

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        tab_id: TabID = TabID.ALL,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
    ):

        self.client_session = client_session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page
        self._tab_id = tab_id

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_tab_id":
                assert_instance(value, TabID, "tab_id")

            case "_subject_type":
                assert_instance(value, SubjectType, "subjct_type")

            case _:
                pass

        super().__setattr__(name, value)

    def _create_payload(self) -> dict[str, str | int]:
        return {
            "keyword": self._query,
            "page": self._page,
            "perPage": self._per_page,
            "subjectType": self._subject_type.value,
            "tabId": self._tab_id,
        }

    async def get_content(self) -> dict:
        contents = await self.client_session.post_to_api(
            self._path, json=self._create_payload()
        )

        target_items = []

        search_results = contents["results"][0]

        if self._subject_type is not SubjectType.ALL:
            for item in search_results["subjects"]:
                if item["subjectType"] == self._subject_type.value:
                    item_name = item["title"]

                    if is_valid_search_item(item_name):
                        item["title"] = sanitize_item_name(item_name)
                        target_items.append(item)
        else:
            target_items = search_results["subjects"]

        contents["items"] = target_items

        if not target_items:
            raise ZeroSearchResultsError(
                "Search yielded empty results. Try a different keyword."
            )

        return contents

    async def get_content_model(self) -> RootSearchResultsModelV2:
        contents = await self.get_content()
        return RootSearchResultsModelV2.model_validate(contents)

    def next_page(self, content: RootSearchResultsModelV2) -> "SearchV2":
        assert_instance(content, RootSearchResultsModelV2, "content")

        if content.pager.has_more:
            return SearchV2(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                tab_id=self._tab_id,
                page=content.pager.next_page,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: RootSearchResultsModelV2) -> "SearchV2":
        assert_instance(content, RootSearchResultsModelV2, "content")

        if content.pager.page >= 2:
            return SearchV2(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                tab_id=self._tab_id,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self,
    ) -> AsyncIterator[RootSearchResultsModelV2]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model()

            yield content_model

            if content_model.pager.has_more:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False


class SeasonDetails:
    """Fetches season information for a particular subject"""

    _path = SEASON_INFO_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        self.client_session = client_session

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case _:
                pass

        super().__setattr__(name, value)

    async def get_content(self, subject_id: str) -> dict:
        if not validate_subject_id(subject_id):
            raise ValueError(f"Invalid subject id passed {subject_id!r}")

        request_params = {"subjectId": subject_id}

        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )
        return contents

    async def get_content_model(self, subject_id: str) -> SeasonsModel:
        contents = await self.get_content(subject_id)
        modelled_contents = SeasonsModel.model_validate(contents)
        return modelled_contents


class ItemDetails:
    """Specific item details including seasons info"""

    _path = SUBJECT_GET_PATH

    def __init__(
        self, client_session: MovieBoxHttpClient, include_seasons: bool = False
    ):
        self.client_session = client_session
        self.include_seasons = include_seasons
        self.season_details = SeasonDetails(client_session)

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "season_details":
                assert_instance(value, SeasonDetails, "season_details")

            case "include_seasons":
                assert type(value) is bool, (
                    f"value for include_seasons must of {type(bool)} not "
                    f"{type(value)}"
                )

            case _:
                pass

        super().__setattr__(name, value)

    async def get_content(
        self,
        subject_id: str,
    ) -> dict:
        if not validate_subject_id(subject_id):
            raise ValueError(f"Invalid subject id passed {subject_id!r}")

        request_params = {"subjectId": subject_id}

        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )

        seasons = None

        if self.include_seasons:
            seasons = await self.season_details.get_content(subject_id)

        contents["seasons"] = seasons

        return contents

    async def get_content_model(
        self,
        subject_id: str,
    ) -> RootItemDetailsModel:
        contents = await self.get_content(subject_id)

        return RootItemDetailsModel.model_validate(contents)


class DownloadableVideoFilesDetail:
    """Fetches downloadable video files detail"""

    _path = RESOURCE_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
        resolution: (
            ResolutionType | CustomResolutionType
        ) = CustomResolutionType.BEST,
    ):
        self.client_session = client_session
        self.page = page
        self.per_page = per_page
        self.resolution = resolution

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "per_page":
                validate_per_page_and_raise(value)

            case "resolution":
                assert_instance(
                    value, (ResolutionType, CustomResolutionType), "resolution"
                )
                if isinstance(value, CustomResolutionType):
                    value = CustomResolutionType.convert_to_default_resolution(
                        value
                    )

            case _:
                pass

        super().__setattr__(name, value)

    def _create_params(self, subject_id: str) -> dict:
        validate_subject_id(subject_id)

        return {
            "subjectId": subject_id,
            "resolution": self.resolution,
            "page": self.page,
            "perPage": self.per_page,
        }

    async def get_content(
        self, subject_id: str, release_date: str = None
    ) -> dict:

        request_params = self._create_params(subject_id)

        contents = await self.client_session.get_from_api(
            self._path,
            params=request_params,
        )
        if release_date:
            contents["releaseDate"] = release_date

        return contents

    async def get_content_model(
        self, subject_id: str, release_date: str = None
    ) -> RootDownloadableFilesDetailModel:
        contents = await self.get_content(subject_id, release_date)

        modelled_contents = RootDownloadableFilesDetailModel.model_validate(
            contents
        )
        return modelled_contents

    def next_page(
        self, content: RootDownloadableFilesDetailModel
    ) -> "DownloadableVideoFilesDetail":
        assert_instance(content, RootDownloadableFilesDetailModel, "content")

        if content.pager.has_more:
            return DownloadableVideoFilesDetail(
                client_session=self.client_session,
                page=content.pager.next_page,
                per_page=self.per_page,
                resolution=self.resolution,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(
        self, content: RootDownloadableFilesDetailModel
    ) -> "DownloadableVideoFilesDetail":
        assert_instance(content, RootDownloadableFilesDetailModel, "content")

        if content.pager.page >= 2:
            return DownloadableVideoFilesDetail(
                client_session=self.client_session,
                page=content.pager.page - 1,
                per_page=self.per_page,
                resolution=self.resolution,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self, subject_id: str
    ) -> AsyncIterator[RootDownloadableFilesDetailModel]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model(subject_id)

            yield content_model

            if content_model.pager.has_more:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False


DownloadableFilesDetail = DownloadableVideoFilesDetail


class DownloadableCaptionFileDetails:
    """Fetches available subtitle files detail for a particular video file"""

    _PATH = EXT_CAPTIONS_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        self.client_session = client_session

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case _:
                pass

        super().__setattr__(name, value)

    def _create_params(
        self,
        subject_id: str,
        resource: VideoFileMetadata | str,
    ) -> dict[str, str]:

        validate_subject_id(subject_id)

        return {
            "subjectId": subject_id,
            "resourceId": (
                resource.resource_id
                if isinstance(resource, VideoFileMetadata)
                else resource
            ),
        }

    async def get_content(
        self,
        subject_id: str,
        resource: VideoFileMetadata | str,
    ) -> dict[str, Any]:

        request_params = self._create_params(subject_id, resource)

        resp = await self.client_session.get_from_api(
            self._PATH, params=request_params
        )

        return resp

    async def get_content_model(
        self,
        subject_id: str,
        resource: VideoFileMetadata | str,
    ) -> RootCaptionFileMetadata:
        content = await self.get_content(subject_id, resource)
        return RootCaptionFileMetadata.model_validate(content)
