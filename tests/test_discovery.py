import pytest
from pathlib import Path
from file_handling.discovery import find_jpg_files


def test_find_jpg_files_empty_dir(source_dir, mock_logger):
    """Test finding JPG files in an empty directory."""
    files = find_jpg_files(source_dir, mock_logger)
    assert len(files) == 0
    mock_logger.warning.assert_called_once()


def test_find_jpg_files(source_dir, mock_logger, sample_jpg_file):
    """Test finding JPG files in a directory with one JPG file."""
    files = find_jpg_files(source_dir, mock_logger)
    assert len(files) == 1
    assert files[0] == sample_jpg_file


def test_find_jpg_files_mixed_content(source_dir, mock_logger, sample_jpg_file):
    """Test finding JPG files in a directory with mixed content."""
    # Create some non-JPG files
    (source_dir / "text_file.txt").write_text("This is a text file")
    (source_dir / "another_file.png").write_bytes(b"fake png data")

    files = find_jpg_files(source_dir, mock_logger)
    assert len(files) == 1
    assert files[0] == sample_jpg_file


def test_find_jpg_files_ignores_hidden(source_dir, mock_logger):
    """Test that find_jpg_files ignores hidden JPG files."""
    hidden_jpg = source_dir / "._hidden.JPG"
    hidden_jpg.write_bytes(b"fake jpg data")

    files = find_jpg_files(source_dir, mock_logger)
    assert len(files) == 0
    mock_logger.warning.assert_called_once()


def test_find_jpg_files_case_insensitive(source_dir, mock_logger):
    """Test that find_jpg_files is case insensitive for JPG extension."""
    upper_jpg = source_dir / "UPPER.JPG"
    upper_jpg.write_bytes(b"fake jpg data")

    lower_jpg = source_dir / "lower.jpg"
    lower_jpg.write_bytes(b"fake jpg data")

    files = find_jpg_files(source_dir, mock_logger)
    assert len(files) == 2
    file_names = [f.name for f in files]
    assert "UPPER.JPG" in file_names
    assert "lower.jpg" in file_names
