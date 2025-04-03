from utils import HashingUtils
import pytest
from unittest.mock import mock_open, patch


def test_get_hash():
    # Test with a valid file
    # Set up test data
    test_file = "test.txt"
    file_content = "Hello, World!"

    # Mock the file open operation so no actual file is created
    with patch(
        "utils.hashing.hashing.open", mock_open(read_data=file_content.encode("utf-8"))
    ):
        expected_hash = HashingUtils.get_hash(test_file)
    assert (
        expected_hash
        == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    )  # SHA256 hash of "Hello, World!"


def test_get_hash_file_not_found():
    # Test with a non-existent file
    with pytest.raises(FileNotFoundError):
        HashingUtils.get_hash("non_existent_file.txt")


def test_get_hash_file_not_readable():
    # Test with a file that cannot be read
    test_file = "test.txt"
    with patch("builtins.open", side_effect=IOError("File not readable")):
        with pytest.raises(IOError):
            HashingUtils.get_hash(test_file)


def test_compare_hashes():
    # Test with a valid file
    # Set up test data
    test_file1 = "test.txt"
    file_content1 = "Hello, World!"
    test_file2 = "test2.txt"
    file_content2 = "Hello, World!"  # Same content to ensure hashes match

    # Create a mock that returns different content based on filename
    def mock_file(filename, *args, **kwargs):
        if filename == test_file1:
            return mock_open(read_data=file_content1.encode("utf-8"))(*args, **kwargs)
        elif filename == test_file2:
            return mock_open(read_data=file_content2.encode("utf-8"))(*args, **kwargs)

    # Mock the file open operation with our custom function
    with patch("utils.hashing.hashing.open", side_effect=mock_file):
        assert HashingUtils.compare_hashes(test_file1, test_file2) is True


def test_compare_hashes_different():
    # Test with non-matching hashes
    # Test with a valid file
    # Set up test data
    test_file1 = "test.txt"
    file_content1 = "Hello, World!"
    test_file2 = "test2.txt"
    file_content2 = "Hello, World"

    # Create a mock that returns different content based on filename
    def mock_file(filename, *args, **kwargs):
        if filename == test_file1:
            return mock_open(read_data=file_content1.encode("utf-8"))(*args, **kwargs)
        elif filename == test_file2:
            return mock_open(read_data=file_content2.encode("utf-8"))(*args, **kwargs)

    # Mock the file open operation with our custom function
    with patch("utils.hashing.hashing.open", side_effect=mock_file):
        assert HashingUtils.compare_hashes(test_file1, test_file2) is False
