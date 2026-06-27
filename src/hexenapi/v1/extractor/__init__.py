"""Extracts data from specific movie/tv-series page"""

from hexenapi.v1.extractor._core import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
    TagDetailsExtractor,
    TagDetailsExtractorModel,
)
from hexenapi.v1.extractor.exceptions import DetailsExtractionError

__all__ = [
    "TagDetailsExtractor",
    "JsonDetailsExtractor",
    "TagDetailsExtractorModel",
    "JsonDetailsExtractorModel",
    "DetailsExtractionError",
]
