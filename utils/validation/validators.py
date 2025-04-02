import logging
from pathlib import Path


def validate_directories(source: Path, destination: Path, log: logging.Logger) -> bool:
    """
    Validate source and destination directories.

    Args:
        source: Source directory path
        destination: Destination directory path
        log: Logger instance

    Returns:
        bool: True if directories are valid, False otherwise
    """
    if not source.exists() or not source.is_dir():
        log.error(f"Source directory {source} does not exist or is not a directory")
        return False

    if not destination.exists():
        log.info(f"Destination directory {destination} does not exist. Creating it.")
        try:
            destination.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.error(f"Failed to create destination directory: {str(e)}")
            return False

    return True
