from datetime import datetime

from PIL import Image

from utils import ExifUtils


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


def test_get_date_taken_heif_file(temp_dir):
    """Test getting date taken from EXIF data in a HEIF file."""
    image_path = temp_dir / "test_image.hif"
    image = Image.new("RGB", (100, 100), color="green")
    exif_data = Image.Exif()
    exif_data[ExifUtils.EXIF_DATETIME_ORIGINAL] = "2023:06:01 10:20:30"

    image.save(image_path, format="HEIF", exif=exif_data)

    date_taken = ExifUtils.get_date_taken(str(image_path))
    assert date_taken == datetime(2023, 6, 1, 10, 20, 30)


def test_get_date_taken_invalid_file(temp_dir):
    """Test getting date taken from an invalid file."""
    invalid_file_path = temp_dir / "invalid_file.txt"
    with open(invalid_file_path, "w") as f:
        f.write("This is not an image file.")

    date_taken = ExifUtils.get_date_taken(str(invalid_file_path))
    assert date_taken is None
