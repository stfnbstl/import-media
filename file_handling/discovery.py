import logging
from pathlib import Path

from utils.validation import FileType


def find_media_files(
    source_path: Path, filetype: FileType, log: logging.Logger
) -> list[Path]:
    """Find all media files with given filetype in the source directory."""
    match filetype:
        case FileType.IMAGE:
            media_files = [
                f
                for f in source_path.iterdir()
                if f.is_file()
                and f.suffix.upper() == ".JPG"
                and not f.name.startswith("._")
            ]
        case FileType.VIDEO:
            media_files = [
                f
                for f in source_path.iterdir()
                if f.is_file()
                and f.suffix.upper() in [".MP4", ".LRF", ".MOV"]
                and not f.name.startswith("._")
            ]

    if not media_files:
        log.warning(f"No JPG files found in {source_path}")

    return media_files
