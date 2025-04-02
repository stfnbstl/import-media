import logging
import shutil
from pathlib import Path

import constants
from utils import HashingUtils


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
    return copy_file(file_path, new_destination_file, log)


def handle_replace_strategy(
    file_path: Path, destination_file: Path, force: bool, log: logging.Logger
) -> bool:
    """Handle the replace strategy for a file."""
    if force:
        log.info(
            f"Replacing file {file_path.name} in {destination_file.parent} (force mode)"
        )
        return copy_file(file_path, destination_file, log)
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
                return copy_file(file_path, destination_file, log)
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


def copy_file(file_path: Path, destination_file: Path, log: logging.Logger) -> bool:
    """Copy a file to a destination path."""
    try:
        shutil.copy2(src=str(file_path), dst=str(destination_file))
        log.info(f"Copied file {file_path.absolute()} to {destination_file.absolute()}")
        return True
    except Exception as e:
        log.error(
            f"Failed to copy {file_path.absolute()} to {destination_file.absolute()}: {str(e)}"
        )
        return False
