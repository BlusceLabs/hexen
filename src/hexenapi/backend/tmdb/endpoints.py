"""All TMDB API v3 endpoints as web-scraping classes, no API key needed."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, urlencode

from hexenapi.backend.tmdb.client import (
    TMDBClient,
    extract_account_states,
    extract_cast,
    extract_changes,
    extract_collection_parts,
    extract_configuration,
    extract_genres,
    extract_images,
    extract_list_items,
    extract_page_data,
    extract_release_dates,
    extract_reviews,
    extract_search_results,
    extract_translations,
    extract_videos,
    extract_watch_providers,
)


def _search_url(path: str, query: str, page: int = 1, **extra) -> str:
    """Build a URL with properly encoded query parameters."""
    params = {"query": query, "page": page}
    params.update({k: v for k, v in extra.items() if v is not None})
    return f"{path}?{urlencode(params)}"


class Movies:
    """GET /movie/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, movie_id: int) -> dict:
        return await self._c.get_page_data(f"/movie/{movie_id}")

    async def account_states(self, movie_id: int) -> dict:
        html = await self._c.get_html(f"/movie/{movie_id}")
        return extract_account_states(html)

    async def alternative_titles(self, movie_id: int) -> list[dict]:
        data = await self.details(movie_id)
        return data.get("alternative_titles", [])

    async def changes(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/changes")
        return extract_changes(html)

    async def credits(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/cast")
        return extract_cast(html)

    async def external_ids(self, movie_id: int) -> dict:
        data = await self.details(movie_id)
        return {k: v for k, v in data.items() if k in ("imdb_id", "twitter", "facebook", "instagram")}

    async def images(self, movie_id: int) -> dict:
        html = await self._c.get_html(f"/movie/{movie_id}/images")
        return extract_images(html)

    async def logos(self, movie_id: int, lang: str = "en") -> list[dict]:
        imgs = await self.images(movie_id)
        return [l for l in imgs.get("logos", []) if lang in l.get("file_path", "")]

    async def keywords(self, movie_id: int) -> list[dict]:
        data = await self.details(movie_id)
        return data.get("keywords", [])

    async def lists(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}")
        return extract_list_items(html, "list")

    async def recommendations(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/recommendations")
        return extract_list_items(html, "movie")

    async def release_dates(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/releases")
        return extract_release_dates(html)

    async def reviews(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/reviews")
        return extract_reviews(html)

    async def similar(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/similar")
        return extract_list_items(html, "movie")

    async def translations(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/translations")
        return extract_translations(html)

    async def videos(self, movie_id: int) -> list[dict]:
        html = await self._c.get_html(f"/movie/{movie_id}/videos")
        return extract_videos(html)

    async def watch_providers(self, movie_id: int) -> dict:
        html = await self._c.get_html(f"/movie/{movie_id}/watch/providers")
        return extract_watch_providers(html)

    async def search(self, query: str, page: int = 1, year: int | None = None) -> list[dict]:
        url = _search_url("/search/movie", query, page, year=year)
        html = await self._c.get_html(url)
        return extract_search_results(html)

    async def popular(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/movie/popular?page={page}")
        return extract_list_items(html, "movie")

    async def top_rated(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/movie/top_rated?page={page}")
        return extract_list_items(html, "movie")

    async def now_playing(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/movie/now_playing?page={page}")
        return extract_list_items(html, "movie")

    async def upcoming(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/movie/upcoming?page={page}")
        return extract_list_items(html, "movie")

    async def latest(self) -> dict:
        return await self._c.get_page_data("/movie/latest")


class TV:
    """GET /tv/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, tv_id: int) -> dict:
        return await self._c.get_page_data(f"/tv/{tv_id}")

    async def account_states(self, tv_id: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}")
        return extract_account_states(html)

    async def aggregate_credits(self, tv_id: int) -> list[dict]:
        return await self.credits(tv_id)

    async def alternative_titles(self, tv_id: int) -> list[dict]:
        data = await self.details(tv_id)
        return data.get("alternative_titles", [])

    async def changes(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/changes")
        return extract_changes(html)

    async def content_ratings(self, tv_id: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}")
        data = {}
        for m in re.finditer(r'certification["\s:]+([^"<,]+)', html):
            data.setdefault("ratings", []).append(m.group(1).strip())
        return data

    async def credits(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/cast")
        return extract_cast(html)

    async def episode_groups(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}")
        return extract_list_items(html, "episode_group")

    async def external_ids(self, tv_id: int) -> dict:
        data = await self.details(tv_id)
        return {k: v for k, v in data.items() if k in ("imdb_id", "twitter", "facebook", "instagram")}

    async def images(self, tv_id: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}/images")
        return extract_images(html)

    async def logos(self, tv_id: int, lang: str = "en") -> list[dict]:
        imgs = await self.images(tv_id)
        return [l for l in imgs.get("logos", []) if lang in l.get("file_path", "")]

    async def keywords(self, tv_id: int) -> list[dict]:
        data = await self.details(tv_id)
        return data.get("keywords", [])

    async def lists(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}")
        return extract_list_items(html, "list")

    async def recommendations(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/recommendations")
        return extract_list_items(html, "tv")

    async def reviews(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/reviews")
        return extract_reviews(html)

    async def screened_theatrically(self, tv_id: int) -> dict:
        return await self.details(tv_id)

    async def similar(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/similar")
        return extract_list_items(html, "tv")

    async def translations(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/translations")
        return extract_translations(html)

    async def videos(self, tv_id: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/videos")
        return extract_videos(html)

    async def watch_providers(self, tv_id: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}/watch/providers")
        return extract_watch_providers(html)

    async def search(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/tv", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)

    async def popular(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/tv/popular?page={page}")
        return extract_list_items(html, "tv")

    async def top_rated(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/tv/top_rated?page={page}")
        return extract_list_items(html, "tv")

    async def airing_today(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/tv/airing_today?page={page}")
        return extract_list_items(html, "tv")

    async def on_the_air(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/tv/on_the_air?page={page}")
        return extract_list_items(html, "tv")

    async def latest(self) -> dict:
        return await self._c.get_page_data("/tv/latest")

    async def season_details(self, tv_id: int, season: int) -> dict:
        return await TVSeason(self._c).details(tv_id, season)

    async def episode_details(self, tv_id: int, season: int, episode: int) -> dict:
        return await TVEpisode(self._c).details(tv_id, season, episode)


class TVSeason:
    """GET /tv/{id}/season/{n} endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, tv_id: int, season: int) -> dict:
        return await self._c.get_page_data(f"/tv/{tv_id}/season/{season}")

    async def changes(self, tv_id: int, season: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}")
        return extract_changes(html)

    async def credits(self, tv_id: int, season: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/cast")
        return extract_cast(html)

    async def external_ids(self, tv_id: int, season: int) -> dict:
        return await self.details(tv_id, season)

    async def images(self, tv_id: int, season: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/images")
        return extract_images(html)

    async def translations(self, tv_id: int, season: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/translations")
        return extract_translations(html)

    async def videos(self, tv_id: int, season: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/videos")
        return extract_videos(html)


class TVEpisode:
    """GET /tv/{id}/season/{n}/episode/{n} endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, tv_id: int, season: int, episode: int) -> dict:
        return await self._c.get_page_data(f"/tv/{tv_id}/season/{season}/episode/{episode}")

    async def account_states(self, tv_id: int, season: int, episode: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}")
        return extract_account_states(html)

    async def changes(self, tv_id: int, season: int, episode: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}")
        return extract_changes(html)

    async def credits(self, tv_id: int, season: int, episode: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}/cast")
        return extract_cast(html)

    async def external_ids(self, tv_id: int, season: int, episode: int) -> dict:
        return await self.details(tv_id, season, episode)

    async def images(self, tv_id: int, season: int, episode: int) -> dict:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}/images")
        return extract_images(html)

    async def translations(self, tv_id: int, season: int, episode: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}/translations")
        return extract_translations(html)

    async def videos(self, tv_id: int, season: int, episode: int) -> list[dict]:
        html = await self._c.get_html(f"/tv/{tv_id}/season/{season}/episode/{episode}/videos")
        return extract_videos(html)


class People:
    """GET /person/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, person_id: int) -> dict:
        return await self._c.get_page_data(f"/person/{person_id}")

    async def changes(self, person_id: int) -> list[dict]:
        html = await self._c.get_html(f"/person/{person_id}/changes")
        return extract_changes(html)

    async def combined_credits(self, person_id: int) -> dict:
        return await self.movie_credits(person_id)

    async def external_ids(self, person_id: int) -> dict:
        data = await self.details(person_id)
        return {k: v for k, v in data.items() if k in ("imdb_id", "twitter", "facebook", "instagram")}

    async def images(self, person_id: int) -> dict:
        html = await self._c.get_html(f"/person/{person_id}/images")
        return extract_images(html)

    async def movie_credits(self, person_id: int) -> list[dict]:
        html = await self._c.get_html(f"/person/{person_id}/movie_credits")
        return extract_list_items(html, "movie")

    async def tv_credits(self, person_id: int) -> list[dict]:
        html = await self._c.get_html(f"/person/{person_id}/tv_credits")
        return extract_list_items(html, "tv")

    async def translations(self, person_id: int) -> list[dict]:
        html = await self._c.get_html(f"/person/{person_id}")
        return extract_translations(html)

    async def popular(self, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/person/popular?page={page}")
        return extract_list_items(html, "person")

    async def latest(self) -> dict:
        return await self._c.get_page_data("/person/latest")

    async def search(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/person", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)


class Search:
    """GET /search/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def multi(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)

    async def movie(self, query: str, page: int = 1, **kw) -> list[dict]:
        return await Movies(self._c).search(query, page, **kw)

    async def tv(self, query: str, page: int = 1) -> list[dict]:
        return await TV(self._c).search(query, page)

    async def person(self, query: str, page: int = 1) -> list[dict]:
        return await People(self._c).search(query, page)

    async def collection(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/collection", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)

    async def company(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/company", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)

    async def keyword(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/keyword", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)


class Discover:
    """GET /discover/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def movies(self, **filters) -> list[dict]:
        clean = {str(k): str(v) for k, v in filters.items() if v is not None}
        html = await self._c.get_html(f"/discover/movie?{urlencode(clean)}")
        return extract_list_items(html, "movie")

    async def tv(self, **filters) -> list[dict]:
        clean = {str(k): str(v) for k, v in filters.items() if v is not None}
        html = await self._c.get_html(f"/discover/tv?{urlencode(clean)}")
        return extract_list_items(html, "tv")


class Trending:
    """GET /trending/* endpoints (falls back to popular).

    NOTE: The ``time_window`` parameter is accepted for API compatibility
    but is currently ignored — scraping doesn't expose per-window trending.
    """

    def __init__(self, c: TMDBClient):
        self._c = c

    async def all(self, time_window: str = "day") -> list[dict]:
        return await Movies(self._c).popular()

    async def movies(self, time_window: str = "day") -> list[dict]:
        return await Movies(self._c).popular()

    async def tv(self, time_window: str = "day") -> list[dict]:
        return await TV(self._c).popular()

    async def people(self, time_window: str = "day") -> list[dict]:
        return await People(self._c).popular()


class Collections:
    """GET /collection/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, collection_id: int) -> dict:
        return await self._c.get_page_data(f"/collection/{collection_id}")

    async def images(self, collection_id: int) -> dict:
        html = await self._c.get_html(f"/collection/{collection_id}")
        return extract_images(html)

    async def parts(self, collection_id: int) -> list[dict]:
        html = await self._c.get_html(f"/collection/{collection_id}")
        return extract_collection_parts(html)


class Companies:
    """GET /company/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, company_id: int) -> dict:
        return await self._c.get_page_data(f"/company/{company_id}")

    async def alternative_names(self, company_id: int) -> list[dict]:
        data = await self.details(company_id)
        return data.get("alternative_titles", [])

    async def images(self, company_id: int) -> dict:
        html = await self._c.get_html(f"/company/{company_id}")
        return extract_images(html)

    async def search(self, query: str, page: int = 1) -> list[dict]:
        url = _search_url("/search/company", query, page)
        html = await self._c.get_html(url)
        return extract_search_results(html)


class Networks:
    """GET /network endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, network_id: int) -> dict:
        return await self._c.get_page_data(f"/network/{network_id}")

    async def search(self, query: str, page: int = 1) -> list[dict]:
        html = await self._c.get_html(f"/search/network?query={query}&page={page}")
        return extract_search_results(html)


class Keywords:
    """GET /keyword/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, keyword_id: int) -> dict:
        return await self._c.get_page_data(f"/keyword/{keyword_id}")

    async def movies(self, keyword_id: int) -> list[dict]:
        html = await self._c.get_html(f"/keyword/{keyword_id}/movies")
        return extract_list_items(html, "movie")

    async def tv(self, keyword_id: int) -> list[dict]:
        html = await self._c.get_html(f"/keyword/{keyword_id}/tv")
        return extract_list_items(html, "tv")


class Find:
    """GET /find/* endpoint."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def by_imdb(self, imdb_id: str) -> list[dict]:
        html = await self._c.get_html(f"/find/{imdb_id}?external_source=imdb_id")
        return extract_search_results(html)


class Lists:
    """GET/POST /list/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self, list_id: int) -> dict:
        return await self._c.get_page_data(f"/list/{list_id}")

    async def item_status(self, list_id: int) -> dict:
        return await self.details(list_id)


class Genres:
    """GET /genre/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def movie_list(self) -> list[dict]:
        html = await self._c.get_html("/genre/movie/list")
        return extract_genres(html)

    async def tv_list(self) -> list[dict]:
        html = await self._c.get_html("/genre/tv/list")
        return extract_genres(html)


class WatchProviders:
    """GET /watch/providers/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def regions(self) -> list[dict]:
        html = await self._c.get_html("/watch/providers")
        return extract_list_items(html, "watch_provider")

    async def movie(self) -> list[dict]:
        html = await self._c.get_html("/watch/providers/movie")
        return extract_list_items(html, "watch_provider")

    async def tv(self) -> list[dict]:
        html = await self._c.get_html("/watch/providers/tv")
        return extract_list_items(html, "watch_provider")


class Configuration:
    """GET /configuration/* endpoints."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def main(self) -> dict:
        html = await self._c.get_html("/")
        return extract_configuration(html)

    async def countries(self) -> list[dict]:
        html = await self._c.get_html("/compare")
        return extract_list_items(html, "country")

    async def jobs(self) -> list[dict]:
        html = await self._c.get_html("/jobs")
        return extract_list_items(html, "job")

    async def languages(self) -> list[dict]:
        html = await self._c.get_html("/compare")
        return extract_list_items(html, "language")

    async def primary_translations(self) -> list[str]:
        return ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP", "ko-KR", "pt-BR", "zh-CN"]

    async def timezones(self) -> list[dict]:
        return [{"iso_3166_1": "US", "zones": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]}]


class Authentication:
    """GET/POST /authentication/* endpoints (limited without API key)."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def request_token(self) -> dict:
        return {"note": "Requires API key — use TMDB website login instead"}

    async def session(self, request_token: str) -> dict:
        return {"note": "Requires API key"}

    async def guest_session(self) -> dict:
        return {"note": "Requires API key"}

    async def delete_session(self, session_id: str) -> dict:
        return {"note": "Requires API key"}


class Account:
    """GET/POST /account/* endpoints (limited without API key)."""

    def __init__(self, c: TMDBClient):
        self._c = c

    async def details(self) -> dict:
        return {"note": "Requires authentication"}

    async def lists(self, account_id: int) -> list[dict]:
        return []

    async def favorite_movies(self, account_id: int) -> list[dict]:
        return []

    async def favorite_tv(self, account_id: int) -> list[dict]:
        return []

    async def rated_movies(self, account_id: int) -> list[dict]:
        return []

    async def rated_tv(self, account_id: int) -> list[dict]:
        return []

    async def rated_tv_episodes(self, account_id: int) -> list[dict]:
        return []

    async def watchlist_movies(self, account_id: int) -> list[dict]:
        return []

    async def watchlist_tv(self, account_id: int) -> list[dict]:
        return []
