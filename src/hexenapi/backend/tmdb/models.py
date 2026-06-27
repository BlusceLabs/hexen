"""Pydantic models for TMDB API v3 responses."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator

MC = {"extra": "forbid", "populate_by_name": True}


class BelongsToCollection(BaseModel):
    model_config = MC
    id: int
    name: str
    poster_path: str | None = None
    backdrop_path: str | None = None


class Genre(BaseModel):
    model_config = MC
    id: int
    name: str


class ProductionCompany(BaseModel):
    model_config = MC
    id: int
    logo_path: str | None = None
    name: str
    origin_country: str


class ProductionCountry(BaseModel):
    model_config = MC
    iso_3166_1: str
    name: str


class SpokenLanguage(BaseModel):
    model_config = MC
    english_name: str
    iso_639_1: str
    name: str


class Movie(BaseModel):
    model_config = MC
    id: int
    title: str
    original_title: str | None = None
    original_language: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    release_date: date | None = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    adult: bool = False
    genre_ids: list[int] = []
    genres: list[Genre] = []
    tagline: str | None = None
    status: str | None = None
    runtime: int | None = None
    budget: int = 0
    revenue: int = 0
    homepage: str | None = None
    imdb_id: str | None = None
    belongs_to_collection: BelongsToCollection | None = None
    production_companies: list[ProductionCompany] = []
    production_countries: list[ProductionCountry] = []
    spoken_languages: list[SpokenLanguage] = []
    video: bool = False
    external_ids: dict[str, Any] | None = None
    keywords: dict[str, Any] | None = None
    credits: dict[str, Any] | None = None
    similar: dict[str, Any] | None = None
    recommendations: dict[str, Any] | None = None
    videos: dict[str, Any] | None = None
    images: dict[str, Any] | None = None
    reviews: dict[str, Any] | None = None
    translations: dict[str, Any] | None = None
    release_dates: dict[str, Any] | None = None
    watch_providers: dict[str, Any] | None = None

    @field_validator("release_date", mode="before")
    def _parse_date(cls, v):
        if not v or v == "":
            return None
        try:
            return date.fromisoformat(v)
        except (ValueError, TypeError):
            return None


class TVShow(BaseModel):
    model_config = MC
    id: int
    name: str
    original_name: str | None = None
    original_language: str | None = None
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    first_air_date: date | None = None
    last_air_date: date | None = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    adult: bool = False
    genre_ids: list[int] = []
    genres: list[Genre] = []
    tagline: str | None = None
    status: str | None = None
    number_of_seasons: int = 0
    number_of_episodes: int = 0
    seasons: list[dict[str, Any]] = []
    episode_run_time: list[int] = []
    homepage: str | None = None
    in_production: bool = False
    languages: list[str] = []
    last_episode_to_air: dict[str, Any] | None = None
    next_episode_to_air: dict[str, Any] | None = None
    networks: list[dict[str, Any]] = []
    production_companies: list[ProductionCompany] = []
    production_countries: list[ProductionCountry] = []
    spoken_languages: list[SpokenLanguage] = []
    created_by: list[dict[str, Any]] = []
    external_ids: dict[str, Any] | None = None
    keywords: dict[str, Any] | None = None
    credits: dict[str, Any] | None = None
    similar: dict[str, Any] | None = None
    recommendations: dict[str, Any] | None = None
    videos: dict[str, Any] | None = None
    images: dict[str, Any] | None = None
    reviews: dict[str, Any] | None = None
    translations: dict[str, Any] | None = None
    content_ratings: dict[str, Any] | None = None
    watch_providers: dict[str, Any] | None = None

    @field_validator("first_air_date", "last_air_date", mode="before")
    def _parse_date(cls, v):
        if not v or v == "":
            return None
        try:
            return date.fromisoformat(v)
        except (ValueError, TypeError):
            return None


class Person(BaseModel):
    model_config = MC
    id: int
    name: str
    profile_path: str | None = None
    known_for_department: str | None = None
    popularity: float = 0.0
    also_known_as: list[str] = []
    gender: int | None = None
    biography: str | None = None
    birthday: date | None = None
    deathday: date | None = None
    place_of_birth: str | None = None
    homepage: str | None = None
    imdb_id: str | None = None
    movie_credits: dict[str, Any] | None = None
    tv_credits: dict[str, Any] | None = None
    external_ids: dict[str, Any] | None = None
    images: dict[str, Any] | None = None

    @field_validator("birthday", "deathday", mode="before")
    def _parse_date(cls, v):
        if not v or v == "":
            return None
        try:
            return date.fromisoformat(v)
        except (ValueError, TypeError):
            return None


class Collection(BaseModel):
    model_config = MC
    id: int
    name: str
    overview: str | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    parts: list[Movie] = []


class Company(BaseModel):
    model_config = MC
    id: int
    name: str
    description: str | None = None
    headquarters: str | None = None
    homepage: str | None = None
    logo_path: str | None = None
    origin_country: str | None = None
    parent_company: dict[str, Any] | None = None


class Network(BaseModel):
    model_config = MC
    id: int
    name: str
    logo_path: str | None = None
    origin_country: str | None = None


class Keyword(BaseModel):
    model_config = MC
    id: int
    name: str


class Review(BaseModel):
    model_config = MC
    id: str
    author: str
    author_details: dict[str, Any] | None = None
    content: str
    created_at: str | None = None
    updated_at: str | None = None
    url: str | None = None
    iso_639_1: str | None = None


class Video(BaseModel):
    model_config = MC
    id: str
    key: str
    name: str
    site: str
    type: str
    official: bool = False
    published_at: str | None = None
    iso_639_1: str | None = None
    iso_3166_1: str | None = None
    size: int | None = None


class WatchProvider(BaseModel):
    model_config = MC
    provider_id: int
    provider_name: str
    logo_path: str | None = None
    display_priority: int = 0


class PagedResults(BaseModel):
    model_config = MC
    page: int = 1
    total_pages: int = 0
    total_results: int = 0
    results: list[Any] = []


class MovieList(PagedResults):
    results: list[Movie] = []


class TVShowList(PagedResults):
    results: list[TVShow] = []


class PersonList(PagedResults):
    results: list[Person] = []


class GenreList(BaseModel):
    model_config = MC
    genres: list[Genre] = []


class SearchMulti(BaseModel):
    model_config = MC
    page: int = 1
    total_pages: int = 0
    total_results: int = 0
    results: list[dict[str, Any]] = []
