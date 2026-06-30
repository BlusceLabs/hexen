"""HexenAPI backend server — serves TMDB + Moviebox data as JSON API."""

import asyncio
import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

logging.basicConfig(level=logging.INFO, format="[hexenapi] %(message)s")
log = logging.getLogger(__name__)


async def fetch_tmdb(path: str, params: dict) -> dict:
    from hexenapi.backend.tmdb import (
        TV,
        Collections,
        Companies,
        Configuration,
        Discover,
        Find,
        Genres,
        Keywords,
        Movies,
        People,
        Search,
        TMDBClient,
        Trending,
        WatchProviders,
    )

    async with TMDBClient() as c:
        parts = path.strip("/").split("/")
        resource = parts[0] if parts else ""

        try:
            if resource == "movie":
                return await _handle_movie(c, parts, params)
            elif resource == "tv":
                return await _handle_tv(c, parts, params)
            elif resource == "person":
                return await _handle_person(c, parts, params)
            elif resource == "search":
                return await _handle_search(c, parts, params)
            elif resource == "discover":
                return await _handle_discover(c, parts, params)
            elif resource == "trending":
                return await _handle_trending(c, parts, params)
            elif resource == "genre":
                return await _handle_genre(c, parts)
            elif resource == "collection":
                return await _handle_collection(c, parts)
            elif resource == "company":
                return await _handle_company(c, parts)
            elif resource == "keyword":
                return await _handle_keyword(c, parts)
            elif resource == "find":
                return await _handle_find(c, parts)
            elif resource == "watch":
                return await _handle_watch(c, parts)
            elif resource == "configuration":
                cfg = Configuration(c)
                return await cfg.main()
            elif resource == "health":
                return {"status": "ok", "version": "1.0.0", "service": "hexenapi"}
            elif resource == "stream":
                return await _handle_stream(path, params)
            elif resource == "proxy":
                return await _handle_stream_proxy(params)
            else:
                return {"error": f"Unknown resource: {resource}"}

        except ValueError as e:
            return {"error": f"Invalid parameter: {e}"}
        except IndexError as e:
            return {"error": f"Missing path segment: {e}"}
        except Exception as e:
            log.error(f"Error handling {path}: {e}")
            return {"error": str(e)}


async def _handle_movie(c, parts, params):
    from hexenapi.backend.tmdb import Movies

    m = Movies(c)
    if len(parts) == 1:
        action = params.get("action", ["popular"])[0]
        page = int(params.get("page", ["1"])[0])
        if action == "popular":
            return {"results": await m.popular(page)}
        if action == "top_rated":
            return {"results": await m.top_rated(page)}
        if action == "now_playing":
            return {"results": await m.now_playing(page)}
        if action == "upcoming":
            return {"results": await m.upcoming(page)}
        if action == "latest":
            return await m.latest()
        return {"error": f"Unknown action: {action}"}
    mid = int(parts[1])
    if len(parts) == 2:
        return await m.details(mid)
    sub = parts[2]
    if sub == "credits":
        return {"cast": await m.credits(mid)}
    if sub == "videos":
        return {"videos": await m.videos(mid)}
    if sub == "images":
        return await m.images(mid)
    if sub == "logos":
        return {"logos": await m.logos(mid)}
    if sub == "reviews":
        return {"reviews": await m.reviews(mid)}
    if sub == "translations":
        return {"translations": await m.translations(mid)}
    if sub == "release_dates":
        return {"release_dates": await m.release_dates(mid)}
    if sub == "watch_providers":
        return {"watch_providers": await m.watch_providers(mid)}
    if sub == "similar":
        return {"results": await m.similar(mid)}
    if sub == "recommendations":
        return {"results": await m.recommendations(mid)}
    if sub == "keywords":
        return {"keywords": await m.keywords(mid)}
    if sub == "alternative_titles":
        return {"titles": await m.alternative_titles(mid)}
    if sub == "external_ids":
        return await m.external_ids(mid)
    if sub == "lists":
        return {"lists": await m.lists(mid)}
    if sub == "changes":
        return {"changes": await m.changes(mid)}
    return {"error": f"Unknown sub-resource: {sub}"}


async def _handle_tv(c, parts, params):
    from hexenapi.backend.tmdb import TV

    tv = TV(c)
    if len(parts) == 1:
        action = params.get("action", ["popular"])[0]
        page = int(params.get("page", ["1"])[0])
        if action == "popular":
            return {"results": await tv.popular(page)}
        if action == "top_rated":
            return {"results": await tv.top_rated(page)}
        if action == "airing_today":
            return {"results": await tv.airing_today(page)}
        if action == "on_the_air":
            return {"results": await tv.on_the_air(page)}
        if action == "latest":
            return await tv.latest()
        return {"error": f"Unknown action: {action}"}
    tid = int(parts[1])
    if len(parts) == 2:
        return await tv.details(tid)
    sub = parts[2]
    if sub == "credits":
        return {"cast": await tv.credits(tid)}
    if sub == "videos":
        return {"videos": await tv.videos(tid)}
    if sub == "images":
        return await tv.images(tid)
    if sub == "logos":
        return {"logos": await tv.logos(tid)}
    if sub == "reviews":
        return {"reviews": await tv.reviews(tid)}
    if sub == "translations":
        return {"translations": await tv.translations(tid)}
    if sub == "watch_providers":
        return {"watch_providers": await tv.watch_providers(tid)}
    if sub == "similar":
        return {"results": await tv.similar(tid)}
    if sub == "recommendations":
        return {"results": await tv.recommendations(tid)}
    if sub == "keywords":
        return {"keywords": await tv.keywords(tid)}
    if sub == "season":
        if len(parts) < 4:
            return {"error": "Missing season number"}
        season = int(parts[3])
        if len(parts) == 4:
            return await tv.season_details(tid, season)
        if len(parts) < 5:
            return {"error": "Missing episode number"}
        ep = int(parts[4])
        return await tv.episode_details(tid, season, ep)
    return {"error": f"Unknown sub-resource: {sub}"}


async def _handle_person(c, parts, params):
    from hexenapi.backend.tmdb import People

    p = People(c)
    if len(parts) == 1:
        page = int(params.get("page", ["1"])[0])
        return {"results": await p.popular(page)}
    pid = int(parts[1])
    if len(parts) == 2:
        return await p.details(pid)
    sub = parts[2]
    if sub == "movie_credits":
        return {"movies": await p.movie_credits(pid)}
    if sub == "tv_credits":
        return {"tv": await p.tv_credits(pid)}
    if sub == "images":
        return await p.images(pid)
    if sub == "external_ids":
        return await p.external_ids(pid)
    if sub == "changes":
        return {"changes": await p.changes(pid)}
    return {"error": f"Unknown sub-resource: {sub}"}


async def _handle_search(c, parts, params):
    from hexenapi.backend.tmdb import Search

    s = Search(c)
    query = params.get("q", [""])[0]
    page = int(params.get("page", ["1"])[0])
    target = params.get("type", ["multi"])[0]
    if target == "multi":
        return {"results": await s.multi(query, page)}
    if target == "movie":
        return {"results": await s.movie(query, page)}
    if target == "tv":
        return {"results": await s.tv(query, page)}
    if target == "person":
        return {"results": await s.person(query, page)}
    if target == "collection":
        return {"results": await s.collection(query, page)}
    if target == "company":
        return {"results": await s.company(query, page)}
    if target == "keyword":
        return {"results": await s.keyword(query, page)}
    return {"error": f"Unknown search type: {target}"}


async def _handle_discover(c, parts, params):
    from hexenapi.backend.tmdb import Discover

    d = Discover(c)
    target = parts[1] if len(parts) > 1 else "movie"
    filters = {k: v[0] for k, v in params.items() if k not in ("action",)}
    if target == "movie":
        return {"results": await d.movies(**filters)}
    if target == "tv":
        return {"results": await d.tv(**filters)}
    return {"error": f"Unknown discover target: {target}"}


async def _handle_trending(c, parts, params):
    from hexenapi.backend.tmdb import Trending

    t = Trending(c)
    target = parts[1] if len(parts) > 1 else "all"
    tw = parts[2] if len(parts) > 2 else "day"
    if target == "all":
        return {"results": await t.all(tw)}
    if target == "movie":
        return {"results": await t.movies(tw)}
    if target == "tv":
        return {"results": await t.tv(tw)}
    if target == "person":
        return {"results": await t.people(tw)}
    return {"error": f"Unknown trending target: {target}"}


async def _handle_genre(c, parts):
    from hexenapi.backend.tmdb import Genres

    g = Genres(c)
    target = parts[1] if len(parts) > 1 else "movie"
    if target == "movie":
        return {"genres": await g.movie_list()}
    if target == "tv":
        return {"genres": await g.tv_list()}
    return {"error": f"Unknown genre target: {target}"}


async def _handle_collection(c, parts):
    from hexenapi.backend.tmdb import Collections

    col = Collections(c)
    cid = int(parts[1])
    if len(parts) == 2:
        return await col.details(cid)
    if len(parts) > 2 and parts[2] == "images":
        return await col.images(cid)
    return {"error": f"Unknown sub-resource: {parts[2]}"}


async def _handle_company(c, parts):
    from hexenapi.backend.tmdb import Companies

    comp = Companies(c)
    cid = int(parts[1])
    if len(parts) == 2:
        return await comp.details(cid)
    if len(parts) > 2 and parts[2] == "images":
        return await comp.images(cid)
    if len(parts) > 2 and parts[2] == "alternative_names":
        return {"names": await comp.alternative_names(cid)}
    return {"error": f"Unknown sub-resource: {parts[2]}"}


async def _handle_keyword(c, parts):
    from hexenapi.backend.tmdb import Keywords

    kw = Keywords(c)
    kid = int(parts[1])
    if len(parts) == 2:
        return await kw.details(kid)
    if len(parts) > 2 and parts[2] == "movies":
        return {"results": await kw.movies(kid)}
    if len(parts) > 2 and parts[2] == "tv":
        return {"results": await kw.tv(kid)}
    return {"error": f"Unknown sub-resource: {parts[2]}"}


async def _handle_find(c, parts):
    from hexenapi.backend.tmdb import Find

    f = Find(c)
    ext_id = parts[1]
    return {"results": await f.by_imdb(ext_id)}


async def _handle_watch(c, parts):
    from hexenapi.backend.tmdb import WatchProviders

    wp = WatchProviders(c)
    target = parts[1] if len(parts) > 1 else "regions"
    if target == "regions":
        return {"regions": await wp.regions()}
    if target == "movie":
        return {"results": await wp.movie()}
    if target == "tv":
        return {"results": await wp.tv()}
    return {"error": f"Unknown target: {target}"}


async def _handle_stream(path: str, params: dict) -> dict:
    """Handle Moviebox streaming: search → get download URLs."""
    from hexenapi.v1.core import Search
    from hexenapi.v1.download import DownloadableMovieFilesDetail
    from hexenapi.v1.requests import Session

    parts = path.strip("/").split("/")
    action = parts[1] if len(parts) > 1 else "info"

    if action == "info":
        query = params.get("q", [""])[0]
        if not query:
            return {"error": "Missing query parameter 'q'"}

        session = Session()
        search = Search(session, query)
        model = await search.get_content_model()

        if not model.items:
            return {"error": "No results found", "results": []}

        item = model.items[0]
        subject_id = item.subjectId
        title = item.title

        try:
            detail = DownloadableMovieFilesDetail(session, item)
            files_model = await detail.get_content_model()
            downloads = []
            for d in files_model.downloads:
                downloads.append(
                    {
                        "url": str(d.url),
                        "resolution": d.resolution,
                        "size": d.size,
                        "ext": d.ext,
                    }
                )
            return {
                "subject_id": subject_id,
                "title": title,
                "has_resource": files_model.hasResource,
                "limited": files_model.limited,
                "downloads": sorted(
                    downloads, key=lambda x: x["resolution"], reverse=True
                ),
            }
        except Exception as e:
            log.error(f"Error fetching stream info for query '{query}': {e}")
            return {
                "subject_id": subject_id,
                "title": title,
                "has_resource": False,
                "error": str(e),
                "downloads": [],
            }

    elif action == "tv":
        query = params.get("q", [""])[0]
        season = int(params.get("season", ["1"])[0])
        episode = int(params.get("episode", ["1"])[0])
        if not query:
            return {"error": "Missing query parameter 'q'"}

        session = Session()
        search = Search(session, query)
        model = await search.get_content_model()

        if not model.items:
            return {"error": "No results found", "results": []}

        item = model.items[0]
        subject_id = item.subjectId
        title = item.title

        try:
            from hexenapi.v1.download import DownloadableTVSeriesFilesDetail

            detail = DownloadableTVSeriesFilesDetail(session, item)
            files_model = await detail.get_content_model(
                season=season, episode=episode
            )
            downloads = []
            for d in files_model.downloads:
                downloads.append(
                    {
                        "url": str(d.url),
                        "resolution": d.resolution,
                        "size": d.size,
                        "ext": d.ext,
                    }
                )
            return {
                "subject_id": subject_id,
                "title": title,
                "season": season,
                "episode": episode,
                "has_resource": files_model.hasResource,
                "limited": files_model.limited,
                "downloads": sorted(
                    downloads, key=lambda x: x["resolution"], reverse=True
                ),
            }
        except Exception as e:
            log.error(
                f"Error fetching TV stream for '{query}' S{season}E{episode}: {e}"
            )
            return {
                "subject_id": subject_id,
                "title": title,
                "error": str(e),
                "downloads": [],
            }

    return {"error": f"Unknown stream action: {action}"}


async def _handle_stream_proxy(params: dict) -> dict:
    """Proxy a video stream with proper referer headers."""
    import httpx

    url = params.get("url", [""])[0]
    if not url:
        return {"error": "Missing 'url' parameter"}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(
                url,
                headers={
                    "Referer": "https://videodownloader.site/",
                    "Origin": "https://videodownloader.site",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/"
                        "20100101 Firefox/137.0"
                    ),
                    "Accept": "*/*",
                },
            )
            if resp.status_code == 200:
                return {
                    "url": str(resp.url),
                    "status": resp.status_code,
                    "content_type": resp.headers.get("content-type", ""),
                    "content_length": len(resp.content),
                }
            return {"error": f"Upstream returned {resp.status_code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


async def stream_video(handler, url: str):
    """Stream video bytes through the backend with proper headers."""
    import httpx

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            req_headers = {
                "Referer": "https://videodownloader.site/",
                "Origin": "https://videodownloader.site",
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/"
                    "20100101 Firefox/137.0"
                ),
                "Accept": "*/*",
            }
            async with client.stream("GET", url, headers=req_headers) as resp:
                if resp.status_code != 200:
                    handler.send_response(resp.status_code)
                    handler.end_headers()
                    return

                handler.send_response(200)
                handler.send_header(
                    "Content-Type", resp.headers.get("content-type", "video/mp4")
                )
                content_length = resp.headers.get("content-length")
                if content_length:
                    handler.send_header("Content-Length", content_length)
                handler.send_header("Access-Control-Allow-Origin", "*")
                handler.send_header("Accept-Ranges", "bytes")
                handler.send_header("Cache-Control", "no-cache")
                handler.end_headers()

                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    handler.wfile.write(chunk)
                    handler.wfile.flush()
    except Exception as e:
        log.error(f"Stream proxy error: {e}")
        try:
            handler.send_response(502)
            handler.end_headers()
        except Exception:
            pass


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Direct video proxy — streams bytes, not JSON
        if path.strip("/") == "proxy":
            url = params.get("url", [""])[0]
            if not url:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Missing url parameter"}).encode()
                )
                return
            
            # Validate URL format
            if not url.startswith(("http://", "https://")):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Invalid URL format"}).encode()
                )
                return
            
            try:
                asyncio.run(stream_video(self, url))
            except Exception as e:
                log.error(f"Stream error: {e}")
                try:
                    self.send_response(502)
                    self.end_headers()
                except Exception:
                    pass
            return

        try:
            result = asyncio.run(fetch_tmdb(path, params))
            status_code = 200
            if isinstance(result, dict) and "error" in result:
                status_code = 400
                if "Unknown resource" in result.get("error", ""):
                    status_code = 404
        except Exception as e:
            log.error(f"Error handling {path}: {e}")
            result = {"error": str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(result, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        log.info(f"{self.client_address[0]} {format % args}")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("0.0.0.0", port), APIHandler)
    log.info(f"HexenAPI backend server running on http://localhost:{port}")
    log.info(
        "Endpoints: /movie, /tv, /person, /search, /discover, /trending, "
        "/genre, /collection, /company, /keyword, /find, /watch, "
        "/configuration, /health"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
