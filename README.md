<div align="center">

# hexenapi

**Unofficial Python wrapper for Moviebox websites and Android app**  
Search, discover, download, and stream movies & TV series with subtitles

[![PyPI version](https://badge.fury.io/py/hexenapi.svg)](https://pypi.org/project/hexenapi)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hexenapi)](https://pypi.org/project/hexenapi)
![Coverage](https://raw.githubusercontent.com/Simatwa/hexenapi/refs/heads/main/assets/coverage.svg)
[![PyPI - License](https://img.shields.io/pypi/l/hexenapi)](https://pypi.org/project/hexenapi)
[![Downloads](https://pepy.tech/badge/hexenapi)](https://pepy.tech/project/hexenapi)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Usage](#usage) • [Documentation](https://hexenapi-docs.netlify.app/)

</div>

## Features

* **Unified Backend** : Single `hexenapi.backend` package consolidating all API versions (H5 web, REST-API, Android app)
* **TMDB Scraper** : Access The Movie Database via web scraping — no API key required (movies, TV, people, search, discover)
* **Download Movies & TV Series** : High-quality downloads with multiple resolution options
* **Subtitle Support** : Download subtitles in multiple languages
* **Faster Downloads** : Up to 5× faster than standard downloads
* **Async & Sync Support** : Fully asynchronous with synchronous fallback
* **Search & Discovery** : Find movies, trending content, and popular searches
* **Developer-Friendly** : Python API with Pydantic models

## Architecture

All API functionality lives in a single unified `backend` package:

```
hexenapi/
├── backend/          # Unified API (all versions consolidated here)
│   ├── core.py       # H5 REST-API (Search, Homepage, ItemDetails)
│   ├── core_v1.py    # Web scraping (Trending, Recommend, PopularSearch)
│   ├── core_v3.py    # Android app API (AppSearch, AppItemDetails)
│   ├── http_client.py# Signed HTTP client with host-pool fallback
│   ├── crypto.py     # Request signing (HMAC-MD5, tokens)
│   ├── download*.py  # Download managers
│   ├── models/       # Pydantic models (details, search, homepage)
│   └── cli/          # CLI commands
├── v1/               # Backwards-compat shim → backend
├── v2/               # Backwards-compat shim → backend
└── v3/               # Backwards-compat shim → backend
```

## Installation

### Base package (for developers)

```sh
uv add hexenapi
```

### Termux (Android)

```sh
pip install hexenapi --no-deps
pip install 'pydantic==2.9.2'
pip install bs4 httpx throttlebuster
```

## Quick Start

### Python API

```python
from hexenapi.backend import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie: {movie_file.saved_to}")
    print(f"Subtitle: {subtitle_file.saved_to}")

asyncio.run(main())
```

## [Usage](https://hexenapi-docs.netlify.app/)

This is just a brief usage information. For more details visit official docs - [https://hexenapi-docs.netlify.app/](https://hexenapi-docs.netlify.app/)

### Python API

#### Simple Auto-Download

```python
from hexenapi.backend import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie saved to: {movie_file.saved_to}")
    print(f"Subtitle saved to: {subtitle_file.saved_to}")

asyncio.run(main())
```

#### Download with Progress Tracking

```python
from hexenapi.backend import DownloadTracker, MovieAuto
import asyncio

async def progress_callback(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100
    print(f"[{percent:.2f}%] Downloading {progress.saved_to.name}", end="\r")

async def main():
    auto = MovieAuto(tasks=1)
    await auto.run("Avatar", progress_hook=progress_callback)

asyncio.run(main())
```

#### Search and Download

```python
from hexenapi.backend import (
    Session, Search, DownloadableSingleFilesDetail,
    MediaFileDownloader, resolve_media_file_to_be_downloaded,
)
import asyncio

async def main():
    session = Session()
    search = Search(session, "Avatar", subject_type=SubjectType.MOVIES)
    results = await search.get_content_model()
    item = results.first_item

    downloader = DownloadableSingleFilesDetail(session, item)
    files = await downloader.get_content_model()

    target = resolve_media_file_to_be_downloaded("BEST", files)
    dl = MediaFileDownloader(dir="./downloads")
    await dl.run(target, item)

asyncio.run(main())
```

#### Android App API (v3-style)

```python
from hexenapi.backend import (
    MovieBoxHttpClient, AndroidSearch, AndroidItemDetails,
    AndroidDownloadableFilesDetail, AndroidMediaFileDownloader,
    android_resolve_media_file, CustomResolutionType,
)
import asyncio

async def main():
    async with MovieBoxHttpClient() as client:
        search = AndroidSearch(client, "Avatar")
        results = await search.get_content_model()
        item = results.first_item

        details = AndroidItemDetails(client)
        item_details = await details.get_content_model(item.subject_id)

        dl_files = AndroidDownloadableFilesDetail(client)
        downloadable = await dl_files.get_content_model(item.subject_id)

        target = android_resolve_media_file(
            CustomResolutionType.BEST, downloadable
        )
        downloader = AndroidMediaFileDownloader(dir="./downloads")
        await downloader.run(target, downloadable)

asyncio.run(main())
```

#### Further Examples

- [V1 Examples](./docs/v1/examples/)
- [V2 Examples](./docs/v2/examples/)

## Mirror Hosts

h5.aoneroom.com has multiple mirror hosts. To use a specific mirror:

```sh
export MOVIEBOX_API_HOST_V2="h5-api.aoneroom.com"
```

## Alternatives

1. Movies - [fzmovies-api](https://github.com/Simatwa/fzmovies-api)
2. TV-Series - [fzseries-api](https://github.com/Simatwa/fzseries-api)


## Mirror Repositories

- [Codeberg](https://codeberg.org/Simatwa/hexenapi)

## Contributors

<div align="center">

<a href="https://github.com/Simatwa/hexenapi/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Simatwa/hexenapi" />
</a>

</div>

<h2 align="center"> Disclaimer </h2>

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content."  
> - *moviebox.ph*

<div align=center>

**Long live Moviebox spirit.**
</div>

<div align="center">Made with ❤️ </div>
