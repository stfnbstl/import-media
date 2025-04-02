import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from file_handling.organization import get_destination_folder


@pytest.fixture
def mock_exif_date():
    """Mock the ExifUtils.get_date_taken function."""
    with patch("file_handling.organization.ExifUtils.get_date_taken") as mock:
        mock.return_value = datetime(2023, 5, 15, 12, 30, 45)
        yield mock


def test_get_destination_folder_with_exif(
    source_dir, destination_dir, mock_logger, mock_exif_date, sample_jpg_file
):
    """Test getting destination folder with valid EXIF data."""
    dest_folder, file_date = get_destination_folder(
        sample_jpg_file, destination_dir, mock_logger
    )

    # Check the returned date matches our mock
    assert file_date == datetime(2023, 5, 15, 12, 30, 45)

    # Check folder structure using locale-aware month name
    month_name = file_date.strftime("%B")  # Gets month name according to locale
    expected_path = destination_dir / "2023" / month_name / "15"
    assert dest_folder == expected_path
    assert dest_folder.exists()


def test_get_destination_folder_without_exif(
    source_dir, destination_dir, mock_logger, sample_jpg_file
):
    """Test getting destination folder when EXIF data is missing."""
    with patch(
        "file_handling.organization.ExifUtils.get_date_taken", return_value=None
    ):
        with patch("file_handling.organization.datetime") as mock_datetime:
            # Set a fixed current date for testing
            mock_now = datetime(2023, 11, 20, 14, 0, 0)
            mock_datetime.now.return_value = mock_now

            dest_folder, file_date = get_destination_folder(
                sample_jpg_file, destination_dir, mock_logger
            )

            # Check the current date was used
            assert file_date == mock_now

            # Check appropriate folder structure with locale-aware month name
            month_name = mock_now.strftime("%B")  # Gets month name according to locale
            expected_path = destination_dir / "2023" / month_name / "20"
            assert dest_folder == expected_path
            assert dest_folder.exists()
            assert dest_folder.exists()


def test_get_destination_folder_creation_error(
    source_dir, destination_dir, mock_logger, mock_exif_date, sample_jpg_file
):
    """Test handling of folder creation errors."""
    with patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")):
        dest_folder, file_date = get_destination_folder(
            sample_jpg_file, destination_dir, mock_logger
        )

        assert dest_folder is None
        assert file_date == datetime(2023, 5, 15, 12, 30, 45)
        mock_logger.error.assert_called_once()
