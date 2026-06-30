"""TMDB web scraper client — no API key required."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TMDB_BASE = "https://www.themoviedb.org"
TMDB_IMG = "https://image.tmdb.org/t/p"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 "
        "Firefox/137.0"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_json_ld_re = re.compile(
    r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', re.S
)


class TMDBClient:
    """Scrapes TMDB website pages. No API key needed."""

    def __init__(self, language: str = "en-US", timeout: float = 15.0, **kw):
        self._language = language
        self._timeout = timeout
        self._httpx_kwargs = kw
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> TMDBClient:
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
            headers=HEADERS,
            **self._httpx_kwargs,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def get_html(self, path: str) -> str:
        assert self._client is not None, "Use 'async with TMDBClient() as c:'"
        resp = await self._client.get(f"{TMDB_BASE}{path}")
        resp.raise_for_status()
        return resp.text

    async def get_page_data(self, path: str) -> dict:
        html = await self.get_html(path)
        return extract_page_data(html)

    def get_sync(self, path: str) -> str:
        import asyncio

        return asyncio.run(self.get_html(path))


def _img_url(path: str, size: str = "w500") -> str:
    if not path:
        return ""
    if path.endswith(".svg"):
        return f"{TMDB_IMG}/original{path}"
    return f"{TMDB_IMG}/{size}{path}"


def extract_page_data(html: str) -> dict:
    json_ld = _extract_json_ld(html) or {}
    extra = _extract_extra_fields(html)
    return {"json_ld": json_ld, **extra}


def _extract_json_ld(html: str) -> dict | None:
    for m in _json_ld_re.findall(html):
        try:
            data = json.loads(m)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _extract_extra_fields(html: str) -> dict:
    data: dict[str, Any] = {}

    m = re.search(r'data-percent="(\d+)"', html)
    if m:
        data["user_rating"] = int(m.group(1))

    m = re.search(r'<img[^>]*class="[^"]*poster[^"]*"[^>]*src="([^"]+)"', html)
    if m:
        data["poster_url"] = m.group(1)

    m = re.search(r'<img[^>]*class="[^"]*backdrop[^"]*"[^>]*src="([^"]+)"', html)
    if m:
        data["backdrop_url"] = m.group(1)

    genres = re.findall(r'/genre/(\d+)-([^"?#]+)', html)
    if genres:
        data["genres"] = [
            {"id": int(gid), "name": name.replace("-", " ").title()}
            for gid, name in dict.fromkeys(genres)
        ]

    m = re.search(
        r'<div[^>]*class="[^"]*overview[^"]*">\s*<p[^>]*>(.*?)</p>', html, re.S
    )
    if m:
        data["overview"] = re.sub(r"<[^>]+>", "", m.group(1)).strip()

    m = re.search(r"Tagline</h3>\s*<p[^>]*>(.*?)</p>", html, re.S)
    if m:
        data["tagline"] = re.sub(r"<[^>]+>", "", m.group(1)).strip()

    imdb = re.search(r"imdb\.com/title/(tt\d+)", html)
    if imdb:
        data["imdb_id"] = imdb.group(1)

    for site, pat in [
        ("twitter", r'twitter\.com/([^"?#]+)'),
        ("facebook", r'facebook\.com/([^"?#]+)'),
        ("instagram", r'instagram\.com/([^"?#]+)'),
    ]:
        m = re.search(pat, html)
        if m:
            data[site] = m.group(1)

    kw = re.findall(r'/keyword/(\d+)-([^"?#]+)', html)
    if kw:
        data["keywords"] = [
            {"id": int(kid), "name": name.replace("-", " ").title()}
            for kid, name in dict.fromkeys(kw)
        ]

    # Alternative titles
    alt_titles = []
    for m in re.finditer(
        r"<td[^>]*>\s*(\w{2})\s*</td>\s*<td[^>]*>(.*?)</td>", html, re.S
    ):
        alt_titles.append(
            {
                "iso_3166_1": m.group(1),
                "title": re.sub(r"<[^>]+>", "", m.group(2)).strip(),
            }
        )
    if alt_titles:
        data["alternative_titles"] = alt_titles

    return data


def extract_images(html: str) -> dict:
    logos, backdrops, posters = [], [], []
    seen = set()
    # First pass: find images explicitly marked with class="logo"
    for m in re.finditer(
        r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*logo[^"]*"', html
    ):
        path = m.group(1)
        fp = path.split("/t/p/")[-1] if "/t/p/" in path else path
        if fp not in seen:
            seen.add(fp)
            logos.append({"file_path": fp, "url": path})
    for m in re.finditer(
        r'<img[^>]*class="[^"]*logo[^"]*"[^>]*src="([^"]+)"', html
    ):
        path = m.group(1)
        fp = path.split("/t/p/")[-1] if "/t/p/" in path else path
        if fp not in seen:
            seen.add(fp)
            logos.append({"file_path": fp, "url": path})

    # Second pass: all images on the page
    for m in re.finditer(
        r'<img[^>]*src="(https://image\.tmdb\.org/t/p/[^"]+)"', html
    ):
        path = m.group(1)
        fp = path.split("/t/p/", 1)[-1] if "/t/p/" in path else path
        if fp in seen:
            continue
        seen.add(fp)
        context = html[max(0, m.start() - 300) : m.start()]
        entry = {"file_path": fp, "url": path}
        if fp.endswith((".svg",)):
            logos.append(entry)
        elif "poster" in context.lower() or re.search(r"/w\d{2,3}/", path):
            posters.append(entry)
        else:
            backdrops.append(entry)
    return {"logos": logos, "backdrops": backdrops, "posters": posters}


def extract_videos(html: str) -> list[dict]:
    videos = []
    seen = set()
    for m in re.finditer(
        r'data-video-key="([^"]+)"[^>]*data-video-type="([^"]*)"', html, re.S
    ):
        key = m.group(1)
        if key in seen:
            continue
        seen.add(key)
        after = html[m.end() : m.end() + 300]
        name_m = re.search(r"<p[^>]*>(.*?)</p>", after, re.S)
        name = re.sub(r"<[^>]+>", "", name_m.group(1)).strip() if name_m else ""
        videos.append(
            {"key": key, "type": m.group(2), "name": name, "site": "YouTube"}
        )
    for m in re.finditer(r'youtube\.com/embed/([^"?&]+)', html):
        key = m.group(1)
        if key not in seen:
            seen.add(key)
            videos.append({"key": key, "site": "YouTube", "type": "Trailer"})
    return videos


def extract_cast(html: str) -> list[dict]:
    cast = []
    seen = set()
    for m in re.finditer(
        r'<a[^>]*href="(/person/(\d+)-([^"]+))"[^>]*>\s*(?:<[^>]*>)*\s*'
        r"(?:<p[^>]*>|<bdi[^>]*>)(.*?)</(?:p|bdi)>",
        html,
        re.S,
    ):
        pid = int(m.group(2))
        if pid in seen:
            continue
        seen.add(pid)
        after = html[m.end() : m.end() + 500]
        char_m = re.search(
            r'(?:class="[^"]*character[^"]*"[^>]*>|>\s*)(.*?)</(?:p|td|div)',
            after,
            re.S,
        )
        character = (
            re.sub(r"<[^>]+>", "", char_m.group(1)).strip() if char_m else ""
        )
        cast.append(
            {
                "id": pid,
                "url": m.group(1),
                "name": re.sub(r"<[^>]+>", "", m.group(4)).strip(),
                "character": character,
            }
        )
    return cast


def extract_reviews(html: str) -> list[dict]:
    reviews = []
    for m in re.finditer(r"<h3[^>]*>(.*?)</h3>", html, re.S):
        author = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not author or len(author) > 60:
            continue
        after = html[m.end() : m.end() + 2000]
        content_m = re.search(r"<p[^>]*>(.*?)</p>", after, re.S)
        content = (
            re.sub(r"<[^>]+>", "", content_m.group(1)).strip()
            if content_m
            else ""
        )
        rating_m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", after[:500])
        rating = float(rating_m.group(1)) if rating_m else None
        reviews.append({"author": author, "content": content, "rating": rating})
    return reviews


def extract_translations(html: str) -> list[dict]:
    translations = []
    for m in re.finditer(
        r"<td[^>]*>\s*(\w{2})\s*</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>",
        html,
        re.S,
    ):
        translations.append(
            {
                "iso_639_1": m.group(1),
                "name": re.sub(r"<[^>]+>", "", m.group(2)).strip(),
                "english_name": re.sub(r"<[^>]+>", "", m.group(3)).strip(),
            }
        )
    return translations


def extract_watch_providers(html: str) -> dict[str, list[dict]]:
    providers: dict[str, list[dict]] = {}
    for region_m in re.finditer(r'data-region="(\w+)"', html):
        region = region_m.group(1)
        after = html[region_m.end() : region_m.end() + 5000]
        items = []
        for pm in re.finditer(
            r'title="([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"', after, re.S
        ):
            items.append({"provider_name": pm.group(1), "logo_url": pm.group(2)})
        if items:
            providers[region] = items
    return providers


def extract_release_dates(html: str) -> list[dict]:
    dates = []
    for m in re.finditer(
        r"<td[^>]*>([\w\s]+?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>",
        html,
        re.S,
    ):
        dates.append(
            {
                "country": m.group(1).strip(),
                "certification": re.sub(r"<[^>]+>", "", m.group(2)).strip(),
                "release_date": re.sub(r"<[^>]+>", "", m.group(3)).strip(),
            }
        )
    return dates


def extract_list_items(html: str, media_type: str = "movie") -> list[dict]:
    results = []
    seen = set()
    pattern = rf"/{media_type}/(\d+)-"
    for mid in re.findall(pattern, html):
        if mid not in seen:
            seen.add(mid)
            results.append({"id": int(mid), "media_type": media_type})
    return results


def extract_search_results(html: str) -> list[dict]:
    results = []
    seen_ids = set()
    for m in re.finditer(r'href="(/(?:movie|tv|person)/(\d+)-([^"]+))"', html):
        mid = int(m.group(2))
        if mid in seen_ids:
            continue
        seen_ids.add(mid)
        media_type = (
            "movie"
            if "/movie/" in m.group(1)
            else "tv" if "/tv/" in m.group(1) else "person"
        )
        after = html[m.end() : m.end() + 300]
        title_m = re.search(
            r"(?:<bdi[^>]*>|<span[^>]*>)(.*?)</(?:bdi|span)>", after, re.S
        )
        title = (
            re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
            if title_m
            else m.group(3).replace("-", " ").title()
        )
        item: dict[str, Any] = {
            "id": mid,
            "url": m.group(1),
            "media_type": media_type,
            "title": title,
        }
        year_m = re.search(r"\((\d{4})\)", after)
        if year_m:
            item["year"] = int(year_m.group(1))
        poster_m = re.search(r'(https://image\.tmdb\.org/t/p/[^"\']+)', after)
        if poster_m:
            item["poster_url"] = poster_m.group(1)
        results.append(item)
    return results


def extract_collection_parts(html: str) -> list[dict]:
    parts = []
    seen = set()
    for m in re.finditer(r'/movie/(\d+)-([^"?#]+)', html):
        mid = m.group(1)
        if mid not in seen:
            seen.add(mid)
            parts.append(
                {"id": int(mid), "title": m.group(2).replace("-", " ").title()}
            )
    return parts


def extract_configuration(html: str) -> dict:
    data: dict[str, Any] = {}
    m = re.search(r"images\.tmdb\.org", html)
    if m:
        data["image_base_url"] = "https://image.tmdb.org/t/p"
    sizes = re.findall(r"(?:w\d+|original|square_\w+)", html)
    if sizes:
        data["poster_sizes"] = list(
            dict.fromkeys(
                [s for s in sizes if s.startswith("w") or s == "original"]
            )
        )
    return data


def extract_genres(html: str) -> list[dict]:
    genres = []
    seen = set()
    for m in re.finditer(r'/genre/(\d+)-([^"?#]+)', html):
        gid = m.group(1)
        if gid not in seen:
            seen.add(gid)
            genres.append(
                {"id": int(gid), "name": m.group(2).replace("-", " ").title()}
            )
    return genres


def extract_account_states(html: str) -> dict:
    data: dict[str, Any] = {}
    m = re.search(r"rated.*?(\d+\.?\d*)", html, re.S)
    if m:
        data["rated"] = float(m.group(1))
    m = re.search(r"watchlist.*?true", html, re.S)
    if m:
        data["watchlist"] = True
    m = re.search(r"favorite.*?true", html, re.S)
    if m:
        data["favorite"] = True
    return data


def extract_changes(html: str) -> list[dict]:
    changes = []
    for m in re.finditer(
        r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', html, re.S
    ):
        changes.append(
            {
                "date": m.group(1),
                "label": re.sub(r"<[^>]+>", "", m.group(2)).strip(),
            }
        )
    return changes
