import pytest
from utils import ExifUtils
from datetime import datetime


def test_get_date_taken(sample_jpg_with_exif):
    """Test getting date taken from EXIF data."""
    date_taken = ExifUtils.get_date_taken(str(sample_jpg_with_exif))
    assert date_taken is not None
    assert isinstance(date_taken, datetime)
    # Check if the date is correct
    # values are based on the sample EXIF data provided
    # in the conftest.py fixture
    assert date_taken.year == 2023
    assert date_taken.month == 1
    assert date_taken.day == 15
    assert date_taken.hour == 12
    assert date_taken.minute == 30
    assert date_taken.second == 45


def test_get_date_taken_no_exif(sample_jpg_file):
    """Test getting date taken from a file without EXIF data."""
    date_taken = ExifUtils.get_date_taken(str(sample_jpg_file))
    assert date_taken is None


def test_get_date_taken_invalid_file(temp_dir):
    """Test getting date taken from an invalid file."""
    invalid_file_path = temp_dir / "invalid_file.txt"
    with open(invalid_file_path, "w") as f:
        f.write("This is not an image file.")

    date_taken = ExifUtils.get_date_taken(str(invalid_file_path))
    assert date_taken is None
