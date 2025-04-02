import pytest
from pathlib import Path
from unittest.mock import patch

from utils.validation.validators import validate_directories


def test_validate_directories_valid(source_dir, destination_dir, mock_logger):
    """Test validation with valid source and destination directories."""
    result = validate_directories(source_dir, destination_dir, mock_logger)
    assert result is True
    mock_logger.error.assert_not_called()


def test_validate_directories_nonexistent_source(temp_dir, mock_logger):
    """Test validation with non-existent source directory."""
    non_existent_source = temp_dir / "non_existent_source"
    destination = temp_dir / "dest"
    destination.mkdir()

    result = validate_directories(non_existent_source, destination, mock_logger)

    assert result is False
    mock_logger.error.assert_called_once()


def test_validate_directories_source_not_directory(temp_dir, mock_logger):
    """Test validation when source is not a directory."""
    source_file = temp_dir / "source_file.txt"
    source_file.write_text("This is not a directory")
    destination = temp_dir / "dest"
    destination.mkdir()

    result = validate_directories(source_file, destination, mock_logger)

    assert result is False
    mock_logger.error.assert_called_once()


def test_validate_directories_create_destination(temp_dir, mock_logger):
    """Test that destination directory is created if it doesn't exist."""
    source = temp_dir / "source"
    source.mkdir()
    destination = temp_dir / "non_existent_dest"

    result = validate_directories(source, destination, mock_logger)

    assert result is True
    assert destination.exists()
    mock_logger.info.assert_called_once()


def test_validate_directories_destination_creation_error(temp_dir, mock_logger):
    """Test handling of destination directory creation errors."""
    source = temp_dir / "source"
    source.mkdir()
    destination = temp_dir / "dest"

    with patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")):
        result = validate_directories(source, destination, mock_logger)

        assert result is False
        mock_logger.error.assert_called_once()
