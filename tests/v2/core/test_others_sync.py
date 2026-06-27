import pytest

from hexenapi.v1.models import SuggestedItemsModel
from hexenapi.v2.core import (
    SearchSuggestion,
    Session,
)
from tests.v2 import MOVIE_KEYWORD


def test_search_suggestion():
    suggestion = SearchSuggestion(Session())
    suggestion_details = suggestion.get_content_model_sync(MOVIE_KEYWORD)
    assert isinstance(suggestion_details, SuggestedItemsModel)
