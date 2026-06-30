"""Smoke test for TMDB web scraping — validates extraction with sample HTML."""

import pytest

from hexenapi.backend.tmdb.client import (
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

# ---------------------------------------------------------------------------
# Sample HTML fixtures (mimics real TMDB page structure)
# ---------------------------------------------------------------------------

MOVIE_DETAIL_HTML = """
<html><head>
<script type="application/ld+json">
{"@type":"Movie","name":"Fight Club","datePublished":"1999-10-15",
"description":"An insomniac office worker and a devil-may-care soap maker.",
"genre":[{"@type":"Genre","name":"Drama"},{"@type":"Genre","name":"Thriller"}],
"aggregateRating":{"ratingValue":8.4},"duration":"PT139M"}
</script></head><body>
<div class="user_score_chart" data-percent="84"></div>
<img class="poster" src="https://image.tmdb.org/t/p/w500/poster.jpg">
<img class="backdrop" src="https://image.tmdb.org/t/p/w1280/bdrop.jpg">
<div class="overview"><p>An insomniac office worker.</p></div>
<h3>Tagline</h3><p>Mischief. Mayhem. Soap.</p>
<a href="https://www.imdb.com/title/tt0137523/">IMDb</a>
<a href="https://twitter.com/fightclub">Twitter</a>
<a href="https://www.facebook.com/fightclub">Facebook</a>
<a href="https://www.instagram.com/fightclub/">Instagram</a>
<a href="/genre/18-Drama">Drama</a>
<a href="/genre/53-Thriller">Thriller</a>
<a href="/keyword/4368-friendship">friendship</a>
<a href="/keyword/818-fight">fight</a>
<a href="/keyword/1234-insomnia">insomnia</a>
</body></html>
"""

IMAGES_HTML = """
<img src="https://image.tmdb.org/t/p/original/mnPy0uGoDmP3ejd0EeR7oyXDnGh.svg"
 class="logo">
<img src="https://image.tmdb.org/t/p/original/fc_logo.png" class="logo">
<img src="https://image.tmdb.org/t/p/w1280/backdrop1.jpg">
<img src="https://image.tmdb.org/t/p/w780/poster1.jpg">
<img src="https://image.tmdb.org/t/p/w500/poster2.jpg">
"""

VIDEOS_HTML = """
<div data-video-key="SzW9jbweXFU" data-video-type="Trailer">
<p>Fight Club Trailer</p></div>
<div data-video-key="QT4CGcC3RQo" data-video-type="Teaser">
<p>Fight Club Teaser</p></div>
<div data-video-key="abc123xyz" data-video-type="Clip">
<p>Opening Scene</p></div>
<iframe src="https://www.youtube.com/embed/SzW9jbweXFU"></iframe>
"""

CAST_HTML = """
<a href="/person/128-brad-pitt"><p>Brad Pitt</p></a> <p>Tyler Durden</p>
<a href="/person/819-edward-norton"><p>Edward Norton</p></a>
<p>The Narrator</p>
<a href="/person/1282-helena-bonham-carter">
<p>Helena Bonham Carter</p></a> <p>Marla Singer</p>
<a href="/person/7623-meat-loaf"><p>Meat Loaf</p></a>
<p>Robert Paulson</p>
"""

REVIEWS_HTML = """
<h3>CinemaFan42</h3>
<p>One of the greatest films ever made. The twist is mind-blowing.</p>
<span>9 / 10</span>
<h3>MovieBuff99</h3>
<p>Fincher at his absolute best. Norton and Pitt deliver.</p>
<span>10 / 10</span>
<h3>FilmCritic2000</h3><p>Overrated but visually stunning.</p>
<span>7 / 10</span>
"""

TRANSLATIONS_HTML = """
<td>en</td><td>English</td><td>English</td>
<td>es</td><td>Español</td><td>Spanish</td>
<td>fr</td><td>Français</td><td>French</td>
<td>de</td><td>Deutsch</td><td>German</td>
"""

SEARCH_HTML = """
<a href="/movie/550-fight-club"><div><bdi>Fight Club</bdi></div></a>
<span>(1999)</span>
<a href="/movie/27205-inception"><div><bdi>Inception</bdi></div></a>
<span>(2010)</span>
<a href="/tv/1399-game-of-thrones"><div><bdi>Game of Thrones</bdi></div></a>
<span>(2011)</span>
<a href="/person/128-brad-pitt"><div><bdi>Brad Pitt</bdi></div></a>
"""

LIST_HTML = """
<a href="/movie/550-fight-club">Fight Club</a>
<a href="/movie/27205-inception">Inception</a>
<a href="/movie/680-pulp-fiction">Pulp Fiction</a>
"""

WATCH_PROVIDERS_HTML = """
<div data-region="US">
<a title="Netflix"><img src="https://image.tmdb.org/t/p/logo/netflix.png"></a>
<a title="Amazon Prime"><img src="https://image.tmdb.org/t/p/logo/amazon.png"></a>
</div>
<div data-region="GB">
<a title="Netflix"><img src="https://image.tmdb.org/t/p/logo/netflix.png"></a>
<a title="Disney+"><img src="https://image.tmdb.org/t/p/logo/disney.png"></a>
</div>
"""

RELEASE_DATES_HTML = """
<td>United States</td><td>R</td><td>1999-10-15</td>
<td>United Kingdom</td><td>18</td><td>1999-11-12</td>
<td>Germany</td><td>FSK 16</td><td>2000-02-10</td>
"""

CHANGES_HTML = """
<time datetime="2024-01-15">January 15, 2024</time>
<time datetime="2024-03-22">March 22, 2024</time>
"""

GENRES_HTML = """
<a href="/genre/28-Action">Action</a>
<a href="/genre/12-Adventure">Adventure</a>
<a href="/genre/16-Animation">Animation</a>
<a href="/genre/35-Comedy">Comedy</a>
<a href="/genre/18-Drama">Drama</a>
"""

COLLECTION_HTML = """
<a href="/movie/550-fight-club">Fight Club</a>
<a href="/movie/551-fight-club-2">Fight Club 2</a>
"""

ACCOUNT_HTML = """
<span class="rated">8.5</span>
<span class="watchlist">true</span>
<span class="favorite">true</span>
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_movie_details():
    data = extract_page_data(MOVIE_DETAIL_HTML)
    jld = data["json_ld"]
    assert jld["name"] == "Fight Club"
    assert jld["datePublished"] == "1999-10-15"
    assert data["user_rating"] == 84
    assert data["tagline"] == "Mischief. Mayhem. Soap."
    assert data["imdb_id"] == "tt0137523"
    assert data["twitter"] == "fightclub"
    assert data["facebook"] == "fightclub"
    assert data["instagram"] == "fightclub/"
    assert len(data["genres"]) == 2
    assert data["genres"][0]["name"] == "Drama"
    assert len(data["keywords"]) == 3
    assert data["poster_url"]
    assert data["backdrop_url"]


def test_images():
    imgs = extract_images(IMAGES_HTML)
    assert len(imgs["logos"]) >= 2
    assert any(".svg" in logo["file_path"] for logo in imgs["logos"])
    assert len(imgs["posters"]) >= 1


def test_videos():
    vids = extract_videos(VIDEOS_HTML)
    keys = {v["key"] for v in vids}
    assert "SzW9jbweXFU" in keys
    assert "QT4CGcC3RQo" in keys
    assert "abc123xyz" in keys
    assert all(v["site"] == "YouTube" for v in vids)
    types = {v["type"] for v in vids}
    assert "Trailer" in types
    assert "Teaser" in types


def test_cast():
    cast = extract_cast(CAST_HTML)
    names = [c["name"] for c in cast]
    assert "Brad Pitt" in names
    assert "Edward Norton" in names
    assert "Helena Bonham Carter" in names
    assert "Meat Loaf" in names
    bp = next(c for c in cast if c["name"] == "Brad Pitt")
    assert bp["character"] == "Tyler Durden"
    assert bp["id"] == 128


def test_reviews():
    revs = extract_reviews(REVIEWS_HTML)
    assert len(revs) == 3
    authors = [r["author"] for r in revs]
    assert "CinemaFan42" in authors
    assert "FilmCritic2000" in authors
    r1 = next(r for r in revs if r["author"] == "CinemaFan42")
    assert r1["rating"] == 9.0
    assert "greatest" in r1["content"]


def test_translations():
    t = extract_translations(TRANSLATIONS_HTML)
    assert len(t) == 4
    langs = [x["iso_639_1"] for x in t]
    assert "en" in langs
    assert "es" in langs
    en = next(x for x in t if x["iso_639_1"] == "en")
    assert en["name"] == "English"


def test_search():
    results = extract_search_results(SEARCH_HTML)
    ids = {r["id"] for r in results}
    assert 550 in ids
    assert 27205 in ids
    assert 1399 in ids
    assert 128 in ids
    fc = next(r for r in results if r["id"] == 550)
    assert fc["media_type"] == "movie"
    assert fc["title"] == "Fight Club"
    got = next(r for r in results if r["id"] == 1399)
    assert got["media_type"] == "tv"


def test_list_items():
    items = extract_list_items(LIST_HTML, "movie")
    ids = {i["id"] for i in items}
    assert 550 in ids
    assert 27205 in ids
    assert 680 in ids
    assert all(i["media_type"] == "movie" for i in items)


def test_watch_providers():
    wp = extract_watch_providers(WATCH_PROVIDERS_HTML)
    assert "US" in wp
    assert "GB" in wp
    us_names = [p["provider_name"] for p in wp["US"]]
    assert "Netflix" in us_names
    assert "Amazon Prime" in us_names
    gb_names = [p["provider_name"] for p in wp["GB"]]
    assert "Disney+" in gb_names


def test_release_dates():
    rd = extract_release_dates(RELEASE_DATES_HTML)
    assert len(rd) == 3
    us = next(r for r in rd if r["country"] == "United States")
    assert us["certification"] == "R"
    assert us["release_date"] == "1999-10-15"


def test_changes():
    ch = extract_changes(CHANGES_HTML)
    assert len(ch) == 2
    assert ch[0]["date"] == "2024-01-15"


def test_genres():
    g = extract_genres(GENRES_HTML)
    assert len(g) == 5
    names = [x["name"] for x in g]
    assert "Action" in names
    assert "Drama" in names
    assert all(isinstance(x["id"], int) for x in g)


def test_collection_parts():
    parts = extract_collection_parts(COLLECTION_HTML)
    assert len(parts) == 2
    ids = {p["id"] for p in parts}
    assert 550 in ids
    assert 551 in ids


def test_account_states():
    st = extract_account_states(ACCOUNT_HTML)
    assert st.get("rated") == 8.5
    assert st.get("watchlist") is True
    assert st.get("favorite") is True


def test_configuration():
    cfg = extract_configuration(
        "<html>image images.tmdb.org w500 w780 original</html>"
    )
    assert "image_base_url" in cfg
