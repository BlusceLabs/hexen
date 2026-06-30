"""V2 Models"""

from __future__ import annotations

from json import loads
from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator

from hexenapi.backend.constants import (
    SubjectType,  # Import SubjectType for forward references
)
from hexenapi.backend.helpers import get_absolute_url
from hexenapi.v1.extractor.models.json import (
    MetadataModel,
    PostListModel,
    ResourceModel,
    StarsModel,
)
from hexenapi.v1.models import (
    ContentCategoryModel,
    ContentImageModel,
    ContentModel,
    PlatformsModel,
    SearchResultsItem as SearchResultsItemV1,
    SearchResultsModel as SearchResultsModelV1,
    TrendingResultsModel,
)


class ContentModelV2(ContentModel):
    """`homepage.operatingList[0].banner.items[0]`"""

    subject: SearchResultsItem | None
    detailPath: str
    url: HttpUrl | None = None

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, value: str):
        return value if bool(value) else None


class ContentCategoryBannerModelV2(BaseModel):
    """`homepage.operatingList[0].banner`"""

    items: list[ContentModelV2]  # list of series/movies


class ContentCategoryModelV2(ContentCategoryModel):
    """`homepage.operatingList[0]`"""

    banner: ContentCategoryBannerModelV2 | None = None
    filters: list[Any]
    customData: Any
    genreTopId: str | None = None
    detailPath: str

    @field_validator("genreTopId", mode="before")
    @classmethod
    def validate_genre_top_id(cls, value):
        return None if not bool(value) else value


class HomepageContentModel(BaseModel):
    """homepage"""

    platformList: list[PlatformsModel] | None = None
    operatingList: list[ContentCategoryModelV2]


class RealContentCategoryModel(TrendingResultsModel):
    title: str


class OPS(BaseModel):
    """`SearchResultsModel.items[0].ops`"""

    trace_id: str
    search_abt: str
    q: str


class DubModel(BaseModel):
    """`SearchResultsModel.items[0].dubs[0]`"""

    subjectId: str
    lanName: str
    lanCode: str
    original: bool
    type: int
    detailPath: str


class SearchResultsItem(SearchResultsItemV1):
    """`SearchResultsModel.items[0]`"""

    subtitles: list[str] | None
    ops: OPS | None
    imdbRatingCount: int | None = None
    stills: ContentImageModel | None = None
    postTitle: str
    season: int
    dubs: list[DubModel] | None = None

    @field_validator("ops", mode="before")
    @classmethod
    def validate_ops(cls, value: str) -> dict:
        if not value:
            return
        return loads(value)

    @field_validator("subtitles", mode="before")
    @classmethod
    def validate_subtitles(cls, value: str) -> list[str]:
        if not value:
            return
        return value.split(",")

    @property
    def page_url(self) -> str:
        """Url to the specific item details"""
        return get_absolute_url(
            f"/wefeed-h5api-bff/detail?detailPath={self.detailPath}"
        )


class SearchResultsModel(SearchResultsModelV1):
    """Whole search results"""

    items: list[SearchResultsItem]

    @property
    def first_item(self) -> SearchResultsItem:
        return self.items[0]


class SpecificItemDetailsModel(BaseModel):
    """For all subjectTypes"""

    subject: SearchResultsItem
    stars: list[StarsModel]
    resource: ResourceModel
    metadata: MetadataModel
    isForbid: bool
    watchTimeLimit: int
    postList: PostListModel
    imdbRatingValue: float  # Fixed: was imbdRate, now matches v1 model


# Rebuild models to resolve forward references
SpecificItemDetailsModel.model_rebuild()