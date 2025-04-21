import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from import_strategies.handlers import (
    handle_rename_strategy,
    handle_replace_strategy,
    handle_onlynew_strategy,
    copy_file,
)
from utils.validation.comparison_mode import ComparisonMode


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


def test_handle_rename_strategy_renamed_file_exists(
    destination_dir, mock_logger, sample_jpg_file
):
    """Test rename strategy when file exists."""
    # First copy the file twice to destination to simulate already renamed existing file
    existing_file = destination_dir / sample_jpg_file.name
    existing_file_renamed = (
        destination_dir / f"{sample_jpg_file.stem}_02{sample_jpg_file.suffix}"
    )
    copy_file(sample_jpg_file, existing_file, MagicMock())
    copy_file(sample_jpg_file, existing_file_renamed, MagicMock())

    # Now test the rename strategy
    result = handle_rename_strategy(sample_jpg_file, destination_dir, mock_logger)

    assert result is True
    renamed_file = (
        destination_dir / f"{sample_jpg_file.stem}_03{sample_jpg_file.suffix}"
    )
    assert renamed_file.exists()


@pytest.mark.parametrize(
    "force,hashes_match,expected_result, comparison_mode",
    [
        (
            True,
            True,
            True,
            ComparisonMode.PARTIAL,
        ),  # Force mode, hashes match, partial hashing
        (
            True,
            False,
            True,
            ComparisonMode.PARTIAL,
        ),  # Force mode, hashes don't match, partial hashing
        (
            False,
            True,
            True,
            ComparisonMode.PARTIAL,
        ),  # Normal mode, hashes match, partial hashing
        (
            False,
            False,
            False,
            ComparisonMode.PARTIAL,
        ),  # Normal mode, hashes don't match, partial hashing
        (
            True,
            True,
            True,
            ComparisonMode.FULL,
        ),  # Force mode, hashes match, full hashing
        (
            True,
            False,
            True,
            ComparisonMode.FULL,
        ),  # Force mode, hashes don't match, full hashing
        (
            False,
            True,
            True,
            ComparisonMode.FULL,
        ),  # Normal mode, hashes match, full hashing
        (
            False,
            False,
            False,
            ComparisonMode.FULL,
        ),  # Normal mode, hashes don't match, full hashing
    ],
)
def test_handle_replace_strategy(
    source_dir,
    destination_dir,
    comparison_mode,
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
        result = handle_replace_strategy(
            sample_jpg_file, dest_file, comparison_mode, force, mock_logger
        )

        assert result is expected_result


def test_handle_replace_strategy_exception(
    destination_dir, sample_jpg_file, mock_logger
):
    dest_file = destination_dir / sample_jpg_file.name
    copy_file(sample_jpg_file, dest_file, MagicMock())
    with patch(
        "import_strategies.handlers.HashingUtils.compare_hashes",
        side_effect=Exception(),
    ):
        with pytest.raises(Exception):
            handle_replace_strategy(sample_jpg_file, dest_file, False, mock_logger)


@pytest.mark.parametrize(
    "force,hashes_match,expected_result,comparison_mode",
    [
        (
            True,
            True,
            False,
            ComparisonMode.PARTIAL,
        ),  # Force mode, hashes match, partial hashing
        (
            True,
            False,
            False,
            ComparisonMode.PARTIAL,
        ),  # Force mode, hashes don't match, partial hashing
        (
            False,
            True,
            False,
            ComparisonMode.PARTIAL,
        ),  # Normal mode, hashes match, partial hashing
        (
            False,
            False,
            False,
            ComparisonMode.PARTIAL,
        ),  # Normal mode, hashes don't match, partial hashing
        (
            True,
            True,
            False,
            ComparisonMode.FULL,
        ),  # Force mode, hashes match, full hashing
        (
            True,
            False,
            False,
            ComparisonMode.FULL,
        ),  # Force mode, hashes don't match, full hashing
        (
            False,
            True,
            False,
            ComparisonMode.FULL,
        ),  # Normal mode, hashes match, full hashing
        (
            False,
            False,
            False,
            ComparisonMode.FULL,
        ),  # Normal mode, hashes don't match, full hashing
    ],
)
def test_handle_onlynew_strategy(
    source_dir,
    destination_dir,
    comparison_mode,
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
        result = handle_onlynew_strategy(
            sample_jpg_file, dest_file, comparison_mode, force, mock_logger
        )

        assert result is expected_result


def test_handle_onlynew_strategy_exception(
    destination_dir, sample_jpg_file, mock_logger
):
    dest_file = destination_dir / sample_jpg_file.name
    copy_file(sample_jpg_file, dest_file, MagicMock())
    with patch(
        "import_strategies.handlers.HashingUtils.compare_hashes",
        side_effect=Exception(),
    ):
        with pytest.raises(Exception):
            handle_onlynew_strategy(sample_jpg_file, dest_file, False, mock_logger)
