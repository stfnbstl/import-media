import logging
from datetime import datetime
from pathlib import Path

from utils import ExifUtils


def get_destination_folder(
    file_path: Path, destination_path: Path, log: logging.Logger
) -> tuple[Path, datetime]:
    """
    Determine destination folder based on EXIF data.

    Returns:
        tuple: (destination_folder_path, file_date)
    """
    # Get the date the file was taken
    cur_file_date = ExifUtils.get_date_taken(str(file_path))
    log.debug(f"Date taken for {file_path.name}: {cur_file_date}")

    # Handle case where EXIF data is missing
    if cur_file_date is None:
        log.warning(f"No EXIF date found for {file_path.name}, using current date")
        cur_file_date = datetime.now()

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
    except Exception as e:
        log.error(f"Failed to create directory {destination_folder}: {str(e)}")
        return None, cur_file_date

    return destination_folder, cur_file_date
