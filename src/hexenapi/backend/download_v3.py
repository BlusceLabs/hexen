"""Makes local copy of remote files (v3 style)"""

from pathlib import Path

import httpx
from throttlebuster import DownloadedFile

from hexenapi.backend._bases import V3FileDownloaderAndHelper
from hexenapi.backend.constants import (
    CustomResolutionType,
    SubjectType,
)
from hexenapi.backend.helpers import assert_instance, get_file_extension
from hexenapi.backend.models.downloadables import (
    CaptionFileMetadata,
    RootDownloadableFilesDetailModel,
    VideoFileMetadata,
)

__all__ = [
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "resolve_media_file_to_be_downloaded",
]


def resolve_media_file_to_be_downloaded(
    resolution: CustomResolutionType,
    downloadable_files_detail: RootDownloadableFilesDetailModel,
) -> VideoFileMetadata:
    """Gets media-file-metadata that matches the target quality. Only for
        movie and other non-series items such as music etc

    Args:
        resolution (CustomResolutionType): Target media resolution
        downloadable_metadata (DownloadableFilesMetadata): Downloadable files
            metadata

    Raises:
        RuntimeError: Incase no media file matched the target quality
        ValueError: Unexpected target media quality

    Returns:
        VideoFileMetadata: Media file details matching the target media quality
    """
    assert_instance(resolution, CustomResolutionType, "resolution")
    if downloadable_files_detail.subject_type is SubjectType.TV_SERIES:
        raise ValueError(
            "Can only process items which falls under non-series "
            f"subject types such as {SubjectType.MOVIES}, {SubjectType.MUSIC} etc"
            f" NOT {downloadable_files_detail.subject_type}"
        )

    match resolution:
        case CustomResolutionType.BEST:
            target_metadata = downloadable_files_detail.best_media_file

        case CustomResolutionType.WORST:
            target_metadata = downloadable_files_detail.worst_media_file

        case _:
            quality_downloads_map = (
                downloadable_files_detail.get_quality_downloads_map()
            )
            target_metadata = quality_downloads_map.get(resolution)

            if target_metadata is None:
                raise RuntimeError(
                    f"Media file for quality {resolution} does not exists. "
                    f"Try other qualities from {quality_downloads_map.keys()}"
                )

    return target_metadata


class MediaFileDownloader(V3FileDownloaderAndHelper):
    """Download movie and tv-series files"""

    movie_filename_template = "{title} ({release_year}).{ext}"
    series_filename_template = "{title} S{season}E{episode}.{ext}"

    possible_filename_placeholders = (
        "{title}",
        "{release_year}",
        "{release_date}",
        "{resolution}",
        "{ext}",
        "{size_string}",
        "{season}",
        "{episode}",
        "{episode_title}",
        "{duration}",
        "{codec_name}",
    )

    def generate_filename(
        self,
        media_file: VideoFileMetadata,
        downloadable_files_detail: RootDownloadableFilesDetailModel,
        test: bool = False,
    ) -> tuple[str, Path]:
        from throttlebuster.helpers import get_filesize_string

        assert_instance(
            downloadable_files_detail,
            RootDownloadableFilesDetailModel,
            "downloadable_files_detail",
        )
        assert_instance(media_file, VideoFileMetadata, "media_file")

        placeholders = dict(
            title=downloadable_files_detail.title,
            release_date=str(downloadable_files_detail.release_date),
            release_year=downloadable_files_detail.release_date.year,
            ext=get_file_extension(media_file.resource_link),
            resolution=media_file.resolution,
            size_string=get_filesize_string(media_file.size),
            season=media_file.season,
            episode=media_file.episode,
            episode_title=media_file.title,
            duration=media_file.duration,
            codec_name=media_file.codec_name,
        )

        filename_template: str = (
            self.series_filename_template
            if downloadable_files_detail.subject_type == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        final_dir = self.create_final_dir(
            working_dir=self.throttle_buster.dir,
            downloadable_files_detail=downloadable_files_detail,
            season=media_file.season,
            episode=media_file.episode,
            test=test,
            group=self.group_series,
        )

        return filename_template.format(**placeholders), final_dir

    async def run(
        self,
        media_file: VideoFileMetadata,
        filename: str | RootDownloadableFilesDetailModel,
        progress_hook: callable = None,
        mode=None,
        disable_progress_bar: bool = None,
        file_size: int = None,
        keep_parts: bool = False,
        timeout_retry_attempts: int = 3,
        colour: str = "cyan",
        simple: bool = False,
        test: bool = False,
        leave: bool = True,
        ascii: bool = False,
        **filename_kwargs,
    ) -> DownloadedFile | httpx.Response:

        assert_instance(media_file, VideoFileMetadata, "media_file")

        dir = None

        if isinstance(filename, RootDownloadableFilesDetailModel):
            filename, dir = self.generate_filename(
                media_file=media_file,
                downloadable_files_detail=filename,
                test=test,
                **filename_kwargs,
            )

        elif self.group_series:
            raise ValueError(
                "Value for filename should be an instance of "
                f"{RootDownloadableFilesDetailModel}"
                " when group_series is activated"
            )

        return await self.throttle_buster.run(
            url=str(media_file.url),
            filename=filename,
            progress_hook=progress_hook,
            mode=mode,
            disable_progress_bar=disable_progress_bar,
            file_size=file_size,
            keep_parts=keep_parts,
            timeout_retry_attempts=timeout_retry_attempts,
            colour=colour,
            simple=simple,
            test=test,
            leave=leave,
            ascii=ascii,
            dir=dir,
        )


class CaptionFileDownloader(V3FileDownloaderAndHelper):
    """Creates a local copy of a remote subtitle/caption file"""

    movie_filename_template = "{title} ({release_year}).{lan}.{ext}"
    series_filename_template = "{title} S{season}E{episode}.{lan}.{ext}"
    possible_filename_placeholders = (
        "{title}",
        "{release_year}",
        "{release_date}",
        "{ext}",
        "{size_string}",
        "{id}",
        "{lan}",
        "{lan_name}",
        "{delay}",
        "{season}",
        "{episode}",
        "{episode_title}",
    )

    def generate_filename(
        self,
        caption_file: CaptionFileMetadata,
        video_file: VideoFileMetadata,
        downloadable_files_detail: RootDownloadableFilesDetailModel,
        test: bool = False,
    ) -> tuple[str, Path]:
        from throttlebuster.helpers import get_filesize_string

        assert_instance(
            downloadable_files_detail,
            RootDownloadableFilesDetailModel,
            "downloadable_files_detail",
        )
        assert_instance(caption_file, CaptionFileMetadata, "caption_file")
        assert_instance(video_file, VideoFileMetadata, "video_file")

        placeholders = dict(
            title=downloadable_files_detail.title,
            release_date=str(downloadable_files_detail.release_date),
            release_year=downloadable_files_detail.release_date.year,
            ext=get_file_extension(str(caption_file.url)),
            size_string=get_filesize_string(caption_file.size),
            id=caption_file.id,
            lan=caption_file.lan,
            lan_name=caption_file.lan_name,
            season=video_file.season,
            episode=video_file.episode,
            episode_title=video_file.title,
        )

        filename_template: str = (
            self.series_filename_template
            if downloadable_files_detail.subject_type == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        final_dir = self.create_final_dir(
            working_dir=self.throttle_buster.dir,
            downloadable_files_detail=downloadable_files_detail,
            season=video_file.season,
            episode=video_file.episode,
            test=test,
            group=self.group_series,
        )

        return filename_template.format(**placeholders), final_dir

    async def run(
        self,
        caption_file: CaptionFileMetadata,
        video_file: VideoFileMetadata,
        downloadable_files_detail: RootDownloadableFilesDetailModel,
        progress_hook: callable = None,
        mode=None,
        disable_progress_bar: bool = None,
        file_size: int = None,
        keep_parts: bool = False,
        timeout_retry_attempts: int = 3,
        colour: str = "cyan",
        simple: bool = False,
        test: bool = False,
        leave: bool = True,
        ascii: bool = False,
        **filename_kwargs,
    ) -> DownloadedFile | httpx.Response:

        dir = None

        filename, dir = self.generate_filename(
            caption_file=caption_file,
            video_file=video_file,
            downloadable_files_detail=downloadable_files_detail,
            test=test,
            **filename_kwargs,
        )

        return await self.throttle_buster.run(
            url=str(caption_file.url),
            filename=filename,
            progress_hook=progress_hook,
            mode=mode,
            disable_progress_bar=disable_progress_bar,
            file_size=file_size,
            keep_parts=keep_parts,
            timeout_retry_attempts=timeout_retry_attempts,
            colour=colour,
            simple=simple,
            test=test,
            leave=leave,
            ascii=ascii,
            dir=dir,
        )
