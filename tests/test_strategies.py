import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from import_strategies.handlers import (
    handle_rename_strategy,
    handle_replace_strategy,
    handle_onlynew_strategy,
    copy_file,
)


def test_copy_file_success(source_dir, destination_dir, mock_logger, sample_jpg_file):
    """Test successful file copy."""
    dest_file = destination_dir / sample_jpg_file.name

    result = copy_file(sample_jpg_file, dest_file, mock_logger)

    assert result is True
    assert dest_file.exists()
    mock_logger.info.assert_called_once()


def test_copy_file_failure(source_dir, destination_dir, mock_logger, sample_jpg_file):
    """Test handling of file copy failure."""
    dest_file = destination_dir / sample_jpg_file.name

    with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
        result = copy_file(sample_jpg_file, dest_file, mock_logger)

        assert result is False
        assert not dest_file.exists()
        mock_logger.error.assert_called_once()


def test_handle_rename_strategy(
    source_dir, destination_dir, mock_logger, sample_jpg_file
):
    """Test rename strategy when file exists."""
    # First copy the file to destination to simulate existing file
    existing_file = destination_dir / sample_jpg_file.name
    copy_file(sample_jpg_file, existing_file, MagicMock())

    # Now test the rename strategy
    result = handle_rename_strategy(sample_jpg_file, destination_dir, mock_logger)

    assert result is True
    renamed_file = (
        destination_dir / f"{sample_jpg_file.stem}_02{sample_jpg_file.suffix}"
    )
    assert renamed_file.exists()


@pytest.mark.parametrize(
    "force,hashes_match,expected_result",
    [
        (True, True, True),  # Force mode, hashes match
        (True, False, True),  # Force mode, hashes don't match
        (False, True, True),  # Normal mode, hashes match
        (False, False, False),  # Normal mode, hashes don't match
    ],
)
def test_handle_replace_strategy(
    source_dir,
    destination_dir,
    mock_logger,
    sample_jpg_file,
    force,
    hashes_match,
    expected_result,
):
    """Test replace strategy with different force and hash scenarios."""
    # Create existing file
    dest_file = destination_dir / sample_jpg_file.name
    copy_file(sample_jpg_file, dest_file, MagicMock())

    with patch(
        "import_strategies.handlers.HashingUtils.compare_hashes",
        return_value=hashes_match,
    ):
        result = handle_replace_strategy(sample_jpg_file, dest_file, force, mock_logger)

        assert result is expected_result


@pytest.mark.parametrize(
    "force,hashes_match,expected_result",
    [
        (True, True, False),  # Force mode, hashes match
        (True, False, False),  # Force mode, hashes don't match
        (False, True, False),  # Normal mode, hashes match
        (False, False, False),  # Normal mode, hashes don't match
    ],
)
def test_handle_onlynew_strategy(
    source_dir,
    destination_dir,
    mock_logger,
    sample_jpg_file,
    force,
    hashes_match,
    expected_result,
):
    """Test onlynew strategy with different force and hash scenarios."""
    # Create existing file
    dest_file = destination_dir / sample_jpg_file.name
    copy_file(sample_jpg_file, dest_file, MagicMock())

    with patch(
        "import_strategies.handlers.HashingUtils.compare_hashes",
        return_value=hashes_match,
    ):
        result = handle_onlynew_strategy(sample_jpg_file, dest_file, force, mock_logger)

        assert result is expected_result
