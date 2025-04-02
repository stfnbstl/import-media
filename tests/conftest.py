import os
import pytest
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image, ExifTags
import logging


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def source_dir(temp_dir):
    """Create a source directory with sample JPG files."""
    source = temp_dir / "source"
    source.mkdir()
    return source


@pytest.fixture
def destination_dir(temp_dir):
    """Create a destination directory."""
    destination = temp_dir / "destination"
    destination.mkdir()
    return destination


@pytest.fixture
def sample_jpg_file(source_dir):
    """Create a sample JPG file with EXIF data."""
    # Create a small test image
    img_path = source_dir / "test_image.jpg"
    img = Image.new("RGB", (100, 100), color="red")

    # Save without EXIF data first
    img.save(img_path)

    return img_path


@pytest.fixture
def sample_jpg_with_exif(source_dir):
    """Create a sample JPG file with EXIF data containing date."""
    img_path = source_dir / "test_image_with_exif.jpg"
    img = Image.new("RGB", (100, 100), color="blue")

    # Create minimal EXIF data with date
    exif_data = {0x9003: "2023:01:15 12:30:45"}  # DateTimeOriginal tag (36867)

    # Save with EXIF data
    img.save(img_path, exif=exif_data)

    return img_path


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock(spec=logging.Logger)
