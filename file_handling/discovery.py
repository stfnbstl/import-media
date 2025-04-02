import logging
from pathlib import Path


def find_jpg_files(source_path: Path, log: logging.Logger) -> list[Path]:
    """Find all JPG files in the source directory."""
    jpg_files = [
        f
        for f in source_path.iterdir()
        if f.is_file() and f.suffix.upper() == ".JPG" and not f.name.startswith("._")
    ]

    if not jpg_files:
        log.warning(f"No JPG files found in {source_path}")

    return jpg_files
