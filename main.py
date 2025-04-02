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
    # Initialize logger with constants.LOG_FORMAT
    log = (
        LoggingUtils.get_base_logger(logging.DEBUG, constants.LOG_FORMAT)
        if verbose
        else LoggingUtils.get_base_logger(logging.INFO, constants.LOG_FORMAT)
    )

    # Validate source and destination directories
    source_path = Path(source).absolute()
    destination_path = Path(destination).absolute()

    if not source_path.exists() or not source_path.is_dir():
        log.error(
            f"Source directory {source_path} does not exist or is not a directory"
        )
        sys.exit(1)

    if not destination_path.exists():
        log.info(
            f"Destination directory {destination_path} does not exist. Creating it."
        )
        try:
            destination_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.error(f"Failed to create destination directory: {str(e)}")
            sys.exit(1)

    log.info(
        f"Importing files with strategy {strategy.name} from {source_path} to {destination_path}"
    )

    # Get all JPG files in the source directory
    src_files = [
        f
        for f in source_path.iterdir()
        if f.is_file() and f.suffix.upper() == ".JPG" and not f.name.startswith("._")
    ]

    if not src_files:
        log.warning(f"No JPG files found in {source_path}")
        return

    # iterate over files and import them
    for file_path in track(src_files, description="Copying files"):
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
            continue

        # create the absolute file path for the destination file
        destination_file = destination_folder / file_path.name

        # Check if the file already exists in the destination folder
        if destination_file.exists():
            if strategy == Strategy.RENAME:
                # For RENAME strategy, don't bother comparing hashes
                # Just append a number to the file name
                i = 2
                while True:
                    new_filename = f"{file_path.stem}_{i:02}{file_path.suffix}"
                    new_destination_file = destination_folder / new_filename
                    if not new_destination_file.exists():
                        break
                    i += 1
                log.debug(f"Renaming file to {new_filename}")
                shutil.copy2(src=str(file_path), dst=str(new_destination_file))
                log.info(f"Copied file {file_path.name} to {new_filename}")
            else:
                # For ONLYNEW and REPLACE strategies
                if force:
                    # Skip hash comparison if force is enabled
                    if strategy == Strategy.ONLYNEW:
                        log.info(
                            f"File {file_path.name} already exists in {destination_folder}. Skipping (force mode)."
                        )
                    elif strategy == Strategy.REPLACE:
                        log.info(
                            f"Replacing file {file_path.name} in {destination_folder} (force mode)"
                        )
                        shutil.copy2(src=str(file_path), dst=str(destination_file))
                        log.info(f"Copied file {file_path.name} to {destination_file}")
                else:
                    # Only compare hashes if force is disabled
                    try:
                        compare_result = HashingUtils.compare_hashes(
                            file1=str(file_path),
                            file2=str(destination_file),
                            buffer_size=constants.BUFFER_SIZE,
                        )

                        if compare_result:
                            log.debug(
                                f"File {file_path.name} is identical to {destination_file}"
                            )

                            if strategy == Strategy.ONLYNEW:
                                log.info(
                                    f"File {file_path.name} already exists in {destination_folder}. Skipping."
                                )
                            elif strategy == Strategy.REPLACE:
                                log.info(
                                    f"Replacing file {file_path.name} in {destination_folder}"
                                )
                                shutil.copy2(
                                    src=str(file_path), dst=str(destination_file)
                                )
                                log.info(
                                    f"Copied file {file_path.name} to {destination_file}"
                                )
                        else:
                            log.warning(
                                f"There is already a file {file_path.name} in {destination_folder} but the hashes do not match. Please check manually."
                            )
                    except Exception as e:
                        log.error(f"Error comparing files: {str(e)}")
                        continue
        else:
            try:
                shutil.copy2(src=str(file_path), dst=str(destination_file))
                log.info(f"Copied file {file_path.name} to {destination_file}")
            except Exception as e:
                log.error(
                    f"Failed to copy {file_path.name} to {destination_file}: {str(e)}"
                )


if __name__ == "__main__":
    app()
