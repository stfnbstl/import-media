import logging
from datetime import datetime
from pathlib import Path

from utils import ExifUtils
from utils.validation.file_types import FileType


def get_destination_folder(
    file_path: Path, destination_path: Path, filetype: FileType, log: logging.Logger
) -> tuple[Path, datetime]:
    """
    Determines and creates the destination folder for a file based on its date.

    For image files, it attempts to use the EXIF 'Date Taken' metadata.
    If EXIF data is unavailable or the file is not an image (e.g., a video),
    it falls back to using the file's last modification timestamp.

    The destination folder structure follows the pattern:
    `destination_path / year / month_name / day`.

    The function also creates the destination directory path if it doesn't exist.

    Args:
        file_path: The Path object representing the source file.
        destination_path: The Path object for the root destination directory.
        filetype: An enum indicating the type of the file (e.g., IMAGE, VIDEO).
        log: A logging.Logger instance for logging operations.

        A tuple containing:
        - The Path object for the determined destination folder. Returns None if
          directory creation fails.
        - The datetime object used to determine the folder structure (either
          EXIF date or modification date).
    """
    # set initial value for cur_file_date to None
    # so it will not fail if the file is a video
    # and we don't have EXIF data
    cur_file_date = None
    # If the file is a video, we don't need to check for EXIF data
    # instead, we leave it None to handle it later
    if filetype == FileType.IMAGE:
        # Get the date the file was taken
        cur_file_date = ExifUtils.get_date_taken(str(file_path))
        log.debug(f"Date taken for {file_path.name}: {cur_file_date}")

    # Handle case where EXIF data is missing
    # or the file is a video in which case cur_file_date is None
    if cur_file_date is None:
        log.debug(
            f"No EXIF date found for {file_path.name}, using modification date instead"
        )
        cur_file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
        log.debug(f"Modification date for {file_path.name}: {cur_file_date}")

    # create the path for the destination folder
    # The folder structure is: destination/year/month/day/files
    destination_folder = (
        destination_path
        / cur_file_date.strftime("%Y")
        / cur_file_date.strftime("%B")
        / cur_file_date.strftime("%d")
    )
    log.debug(f"Destination folder for file {file_path.name}: {destination_folder}")

    # Create the destination folder
    try:
        destination_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory {destination_folder}")
    except Exception as e:
        log.error(f"Failed to create directory {destination_folder}: {str(e)}")
        return None, cur_file_date

    return destination_folder, cur_file_date
