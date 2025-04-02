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

    # Test with a non-existent file
    with pytest.raises(FileNotFoundError):
        HashingUtils.get_hash("non_existent_file.txt")

    # Test with a file that cannot be read
    # This is platform-dependent and may not be possible to simulate in a cross-platform way.
    # You can create a read-protected file on your system and test this case.
