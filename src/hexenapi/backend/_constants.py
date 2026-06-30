"""This module contains constants that are shared between v1 and v2."""

from enum import IntEnum, StrEnum


class SubjectType(IntEnum):
    """Content types mapped to their integer representatives"""

    ALL = 0
    """Both Movies, series and music contents"""

    MOVIES = 1
    """Movies content only"""

    TV_SERIES = 2
    """TV Series content only"""

    EDUCATION = 5
    """Anime contents only"""

    MUSIC = 6  # AUDIO
    """Music contents only"""

    ANIME = 7  # "ShortTV"
    """Anime contents only"""

    OTHER = 8
    """Other contents"""

    UNKNOWN = 9
    """Unknown contents"""

    @classmethod
    def map(cls, ignore_names: set[str] | None = None) -> dict[str, int]:
        """Content-type names mapped to their int representatives"""
        ignore_names = ignore_names or set()
        resp = {}
        for entry in cls:
            if entry.name in ignore_names:
                continue
            resp[entry.name] = entry.value
        return resp


class DownloadStatus(StrEnum):
    DOWNLOADING = "downloading"
    FINISHED = "finished"