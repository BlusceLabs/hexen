"""
TMDB (The Movie Database) — web scraping, no API key required.

Covers every public TMDB API v3 route via web scraping.

Usage::

    from hexenapi.backend.tmdb import TMDBClient, Movies, Search, TV

    async with TMDBClient() as c:
        m = Movies(c)
        details = await m.details(550)
        logos = await m.logos(550)
        cast = await m.credits(550)

        results = await Search(c).movie("Fight Club")

        tv = TV(c)
        show = await tv.details(1399)
"""

from hexenapi.backend.tmdb.client import TMDBClient
from hexenapi.backend.tmdb.endpoints import (
    TV,
    Account,
    Authentication,
    Collections,
    Companies,
    Configuration,
    Discover,
    Find,
    Genres,
    Keywords,
    Lists,
    Movies,
    Networks,
    People,
    Search,
    Trending,
    TVEpisode,
    TVSeason,
    WatchProviders,
)

__all__ = [
    "TMDBClient",
    "Movies",
    "TV",
    "TVSeason",
    "TVEpisode",
    "People",
    "Search",
    "Discover",
    "Trending",
    "Genres",
    "Collections",
    "Companies",
    "Networks",
    "Keywords",
    "Find",
    "Lists",
    "WatchProviders",
    "Configuration",
    "Authentication",
    "Account",
]
