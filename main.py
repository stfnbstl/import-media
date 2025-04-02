import locale
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.progress import track
from typing_extensions import Annotated

import constants
from import_options.strategy import Strategy
from utils import HashingUtils, LoggingUtils, ExifUtils

# Try to set locale, but don't fail if it's not available
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    print("Warning: German locale not available, using system default")

# Define the Typer app
app = typer.Typer(rich_markup_mode="rich")


def setup_logging(verbose: bool) -> logging.Logger:
    """Set up and return a logger with the appropriate log level."""
    return (
        LoggingUtils.get_base_logger(logging.DEBUG, constants.LOG_FORMAT)
        if verbose
        else LoggingUtils.get_base_logger(logging.INFO, constants.LOG_FORMAT)
    )


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


def handle_rename_strategy(
    file_path: Path, destination_folder: Path, log: logging.Logger
) -> bool:
    """Handle the rename strategy for a file."""
    i = 2
    while True:
        new_filename = f"{file_path.stem}_{i:02}{file_path.suffix}"
        new_destination_file = destination_folder / new_filename
        if not new_destination_file.exists():
            break
        i += 1

    log.debug(f"Renaming file to {new_filename}")
    try:
        shutil.copy2(src=str(file_path), dst=str(new_destination_file))
        log.info(f"Copied file {file_path.name} to {new_filename}")
        return True
    except Exception as e:
        log.error(f"Failed to copy {file_path.name} to {new_filename}: {str(e)}")
        return False


def handle_replace_strategy(
    file_path: Path, destination_file: Path, force: bool, log: logging.Logger
) -> bool:
    """Handle the replace strategy for a file."""
    if force:
        log.info(
            f"Replacing file {file_path.name} in {destination_file.parent} (force mode)"
        )
        try:
            shutil.copy2(src=str(file_path), dst=str(destination_file))
            log.info(f"Copied file {file_path.name} to {destination_file}")
            return True
        except Exception as e:
            log.error(
                f"Failed to copy {file_path.name} to {destination_file}: {str(e)}"
            )
            return False
    else:
        try:
            compare_result = HashingUtils.compare_hashes(
                file1=str(file_path),
                file2=str(destination_file),
                buffer_size=constants.BUFFER_SIZE,
            )

            if compare_result:
                log.debug(f"File {file_path.name} is identical to {destination_file}")
                log.info(
                    f"Replacing file {file_path.name} in {destination_file.parent}"
                )
                try:
                    shutil.copy2(src=str(file_path), dst=str(destination_file))
                    log.info(f"Copied file {file_path.name} to {destination_file}")
                    return True
                except Exception as e:
                    log.error(
                        f"Failed to copy {file_path.name} to {destination_file}: {str(e)}"
                    )
                    return False
            else:
                log.warning(
                    f"There is already a file {file_path.name} in {destination_file.parent} but the hashes do not match. Please check manually."
                )
                return False
        except Exception as e:
            log.error(f"Error comparing files: {str(e)}")
            return False


def handle_onlynew_strategy(
    file_path: Path, destination_file: Path, force: bool, log: logging.Logger
) -> bool:
    """Handle the onlynew strategy for a file."""
    if force:
        log.info(
            f"File {file_path.name} already exists in {destination_file.parent}. Skipping (force mode)."
        )
        return False
    else:
        try:
            compare_result = HashingUtils.compare_hashes(
                file1=str(file_path),
                file2=str(destination_file),
                buffer_size=constants.BUFFER_SIZE,
            )

            if compare_result:
                log.debug(f"File {file_path.name} is identical to {destination_file}")
                log.info(
                    f"File {file_path.name} already exists in {destination_file.parent}. Skipping."
                )
                return False
            else:
                log.warning(
                    f"There is already a file {file_path.name} in {destination_file.parent} but the hashes do not match. Please check manually."
                )
                return False
        except Exception as e:
            log.error(f"Error comparing files: {str(e)}")
            return False


def copy_new_file(file_path: Path, destination_file: Path, log: logging.Logger) -> bool:
    """Copy a file to a destination that doesn't already have the file."""
    try:
        shutil.copy2(src=str(file_path), dst=str(destination_file))
        log.info(f"Copied file {file_path.name} to {destination_file}")
        return True
    except Exception as e:
        log.error(f"Failed to copy {file_path.name} to {destination_file}: {str(e)}")
        return False


@app.command()
def import_files(
    source: Annotated[str, typer.Option(help=constants.SOURCE_DESCRIPTION)],
    destination: Annotated[str, typer.Option(help=constants.DESTINATION_DESCRIPTION)],
    strategy: Annotated[
        Strategy, typer.Option(help=constants.STRATEGY_DESCRIPTION)
    ] = Strategy.ONLYNEW,
    verbose: Annotated[bool, typer.Option(help="Enable verbose mode")] = False,
    force: Annotated[
        bool,
        typer.Option(
            help="Skip hash comparison when replacing or checking for new files"
        ),
    ] = False,
):
    """
    Import JPG files from source directory to destination directory,
    organizing them by date taken (from EXIF data) in a year/month/day folder structure.

    Files are handled according to the specified strategy (replace, onlynew, or rename).
    Use force option to skip hash comparison when replacing files or checking for duplicates.
    """
    # Setup logging
    log = setup_logging(verbose)

    # Validate directories
    source_path = Path(source).absolute()
    destination_path = Path(destination).absolute()

    if not validate_directories(source_path, destination_path, log):
        sys.exit(1)

    log.info(
        f"Importing files with strategy {strategy.name} from {source_path} to {destination_path}"
    )

    # Get all JPG files
    src_files = find_jpg_files(source_path, log)

    if not src_files:
        return

    # Process each file
    for file_path in track(src_files, description="Copying files"):
        destination_folder, _ = get_destination_folder(file_path, destination_path, log)

        if destination_folder is None:
            continue

        destination_file = destination_folder / file_path.name

        # Handle file based on strategy
        if destination_file.exists():
            if strategy == Strategy.RENAME:
                handle_rename_strategy(file_path, destination_folder, log)
            elif strategy == Strategy.REPLACE:
                handle_replace_strategy(file_path, destination_file, force, log)
            elif strategy == Strategy.ONLYNEW:
                handle_onlynew_strategy(file_path, destination_file, force, log)
        else:
            copy_new_file(file_path, destination_file, log)


if __name__ == "__main__":
    app()
