import importlib
import locale
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import main
from import_options.strategy import Strategy
from utils.validation.file_types import FileType


@pytest.fixture
def mock_find_media_files():
    """Mock the find_jpg_files function."""
    with patch("main.find_media_files") as mock:
        yield mock


@pytest.fixture
def mock_get_destination_folder():
    """Mock the get_destination_folder function."""
    with patch("main.get_destination_folder") as mock:
        yield mock


@pytest.fixture
def mock_copy_file():
    """Mock the copy_file function."""
    with patch("main.copy_file") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_handle_strategies():
    """Mock all strategy handler functions."""
    with patch("main.handle_rename_strategy") as mock_rename, patch(
        "main.handle_replace_strategy"
    ) as mock_replace, patch("main.handle_onlynew_strategy") as mock_onlynew:
        mock_rename.return_value = True
        mock_replace.return_value = True
        mock_onlynew.return_value = True
        yield (mock_rename, mock_replace, mock_onlynew)


def test_setup_logging_verbose():
    """Test setting up logging with verbose mode."""
    with patch("main.LoggingUtils.get_base_logger") as mock_logger:
        main.setup_logging(True)
        mock_logger.assert_called_with(pytest.approx(10), main.constants.LOG_FORMAT)


def test_setup_logging_normal():
    """Test setting up logging without verbose mode."""
    with patch("main.LoggingUtils.get_base_logger") as mock_logger:
        main.setup_logging(False)
        mock_logger.assert_called_with(pytest.approx(20), main.constants.LOG_FORMAT)


def test_import_files_validation_failure():
    """Test handling of directory validation failure."""
    with patch("main.validate_directories", return_value=False), patch(
        "main.setup_logging"
    ):
        result = main.import_files(
            "invalid/source", "invalid/dest", Strategy.ONLYNEW, False, False
        )
        assert (
            result is False
        )  # Should return False on validation failure instead of exiting


def test_import_files_no_files_found(mock_find_media_files):
    """Test handling when no JPG files are found."""
    mock_find_media_files.return_value = []

    with patch("main.validate_directories", return_value=True), patch(
        "main.setup_logging"
    ):

        result = main.import_files(
            source="/valid/source",
            destination="/valid/dest",
            filetype=FileType.IMAGE,
            strategy=Strategy.ONLYNEW,
            force=False,
            verbose=False,
        )
        assert result is None


@pytest.mark.parametrize(
    "strategy", [Strategy.REPLACE, Strategy.ONLYNEW, Strategy.RENAME]
)
def test_import_files_with_existing_file(
    strategy,
    mock_find_media_files,
    mock_get_destination_folder,
    mock_handle_strategies,
    temp_dir,
):
    """Test importing files with each strategy when destination file exists."""
    # Setup test data
    source_file = Path("/mock/source/file.jpg")
    dest_folder = temp_dir / "2023" / "May" / "15"
    mock_find_media_files.return_value = [source_file]
    mock_get_destination_folder.return_value = (dest_folder, None)

    mock_rename, mock_replace, mock_onlynew = mock_handle_strategies

    # Create the folder and make file appear to exist
    with patch("pathlib.Path.exists", return_value=True), patch(
        "main.validate_directories", return_value=True
    ), patch("main.setup_logging"):

        main.import_files(
            source="/valid/source",
            destination="/valid/dest",
            strategy=strategy,
            filetype=FileType.IMAGE,
            verbose=False,
            force=False,
        )

        # Check appropriate strategy handler was called
        if strategy == Strategy.RENAME:
            mock_rename.assert_called_once()
        elif strategy == Strategy.REPLACE:
            mock_replace.assert_called_once()
        elif strategy == Strategy.ONLYNEW:
            mock_onlynew.assert_called_once()


def test_import_files_with_new_file(
    mock_find_media_files, mock_get_destination_folder, mock_copy_file, temp_dir
):
    """Test importing a new file (not existing in destination)."""
    # Setup test data
    source_file = Path("/mock/source/file.jpg")
    dest_folder = temp_dir / "2023" / "May" / "15"
    mock_find_media_files.return_value = [source_file]
    mock_get_destination_folder.return_value = (dest_folder, None)

    # Make file appear to not exist
    with patch("pathlib.Path.exists", return_value=False), patch(
        "main.validate_directories", return_value=True
    ), patch("main.setup_logging"):

        main.import_files(
            source="/valid/source",
            destination="/valid/dest",
            strategy=Strategy.ONLYNEW,
            filetype=FileType.IMAGE,
            verbose=False,
            force=False,
        )

        # Check copy_file was called
        mock_copy_file.assert_called_once()


def test_import_files_with_destination_folder_none(
    mock_find_media_files, mock_get_destination_folder
):
    """Test handling when get_destination_folder returns None."""
    # Setup test data
    source_file = Path("/mock/source/file.jpg")
    mock_find_media_files.return_value = [source_file]
    mock_get_destination_folder.return_value = (None, None)

    with patch("main.validate_directories", return_value=True), patch(
        "main.setup_logging"
    ), patch("main.copy_file") as mock_copy:

        main.import_files(
            source="/valid/source",
            destination="/valid/dest",
            strategy=Strategy.ONLYNEW,
            filetype=FileType.IMAGE,
            verbose=False,
            force=False,
        )

        # Check copy_file was not called
        mock_copy.assert_not_called()


def test_locale_handling():
    """Test locale handling with both success and failure cases."""
    # Test when locale setting succeeds
    with patch("locale.setlocale") as mock_setlocale, patch(
        "builtins.print"
    ) as mock_print:
        # Reset module to test import behavior
        if "main" in sys.modules:
            del sys.modules["main"]

        # Import should succeed and not print warning
        importlib.import_module("main")
        mock_setlocale.assert_called_once_with(locale.LC_TIME, "de_DE.UTF-8")
        mock_print.assert_not_called()

    # Test when locale setting fails
    with patch("locale.setlocale", side_effect=locale.Error("Test error")), patch(
        "builtins.print"
    ) as mock_print:
        # Reset module to test import behavior
        if "main" in sys.modules:
            del sys.modules["main"]

        # Import should still succeed but print warning
        importlib.import_module("main")
        mock_print.assert_called_once()
        assert "Warning: German locale not available" in mock_print.call_args[0][0]
