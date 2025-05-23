import locale
import logging
from pathlib import Path

import typer
from rich.progress import track
from typing import Annotated

import constants
from file_handling import find_media_files, get_destination_folder
from import_options.strategy import Strategy
from import_strategies import (
    copy_file,
    handle_onlynew_strategy,
    handle_rename_strategy,
    handle_replace_strategy,
)
from utils import LoggingUtils
from utils.validation import validate_directories, FileType
from utils.validation.comparison_mode import ComparisonMode

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


@app.command()
def import_files(
    source: Annotated[str, typer.Option(help=constants.SOURCE_DESCRIPTION)],
    destination: Annotated[str, typer.Option(help=constants.DESTINATION_DESCRIPTION)],
    filetype: Annotated[
        FileType, typer.Option(help=constants.FILETYPE_DESCRIPTION)
    ] = FileType.IMAGE,
    strategy: Annotated[
        Strategy, typer.Option(help=constants.STRATEGY_DESCRIPTION)
    ] = Strategy.ONLYNEW,
    comparison_mode: Annotated[
        ComparisonMode, typer.Option(help=constants.COMPARISON_MODE_DESCRIPTION)
    ] = ComparisonMode.PARTIAL,
    verbose: Annotated[bool, typer.Option(help=constants.VERBOSE_DESCRIPTION)] = False,
    force: Annotated[
        bool,
        typer.Option(
            help=constants.FORCE_DESCRIPTION,
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
        log.error("Directory validation failed. Exiting.")
        return False  # Explicitly return False on validation failure

    log.info(
        f"Importing {filetype.name} files with strategy {strategy.name} from {source_path} to {destination_path}"
    )

    src_files = find_media_files(source_path=source_path, filetype=filetype, log=log)

    if not src_files:
        return

    # Process each file
    for file_path in track(src_files, description="Copying files"):
        destination_folder, _ = get_destination_folder(
            file_path=file_path,
            destination_path=destination_path,
            filetype=filetype,
            log=log,
        )

        if destination_folder is None:
            continue

        destination_file = destination_folder / file_path.name

        # Handle file based on strategy
        if destination_file.exists():
            if strategy == Strategy.RENAME:
                handle_rename_strategy(file_path, destination_folder, log)
            elif strategy == Strategy.REPLACE:
                handle_replace_strategy(
                    file_path, destination_file, comparison_mode, force, log
                )
            elif strategy == Strategy.ONLYNEW:
                handle_onlynew_strategy(
                    file_path, destination_file, comparison_mode, force, log
                )
        else:
            copy_file(file_path, destination_file, log)


if __name__ == "__main__":
    app()
