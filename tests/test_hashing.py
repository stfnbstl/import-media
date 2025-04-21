from utils import HashingUtils
import pytest
from unittest.mock import mock_open, patch
import os

from utils.validation.comparison_mode import ComparisonMode


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
        with patch("os.path.getsize") as mock_getsize:
            # Mock the os.getsize to return the same size for both files
            mock_getsize.side_effect = lambda x: len(file_content1.encode("utf-8"))
            # Call the compare_hashes method
            # Assert that the hashes are the same
            assert (
                HashingUtils.compare_hashes(
                    test_file1, test_file2, ComparisonMode.PARTIAL
                )
                is True
            )


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
        with patch("os.path.getsize") as mock_getsize:
            # Mock the os.getsize to return the same size for both files
            mock_getsize.side_effect = lambda x: len(file_content1.encode("utf-8"))
            # Call the compare_hashes method
            # Assert that the hashes are different
            assert (
                HashingUtils.compare_hashes(
                    test_file1, test_file2, ComparisonMode.PARTIAL
                )
                is False
            )


def test_compare_hashes_different_sizes():
    # Test with files of different sizes
    test_file1 = "test.txt"
    test_file2 = "test2.txt"

    # Mock the os.path.getsize to return different sizes for the two files
    with patch("os.path.getsize") as mock_getsize:
        mock_getsize.side_effect = [100, 200]  # Different sizes
        assert (
            HashingUtils.compare_hashes(test_file1, test_file2, ComparisonMode.PARTIAL)
            is False
        )


def test_compare_hashes_file_not_readable():
    # Test with a file that cannot be read
    test_file1 = "test.txt"
    test_file2 = "test2.txt"

    # Mock the os.path.getsize to return the same size for both files
    with patch("os.path.getsize") as mock_getsize:
        mock_getsize.side_effect = [100, 100]  # Same size
        with patch("builtins.open", side_effect=IOError("File not readable")):
            with pytest.raises(IOError):
                HashingUtils.compare_hashes(
                    test_file1, test_file2, ComparisonMode.PARTIAL
                )


def test_compare_hashes_full_mode_identical():
    # Test with identical files using FULL comparison mode
    test_file1 = "test1.txt"
    file_content1 = b"Identical content"
    test_file2 = "test2.txt"
    file_content2 = b"Identical content"

    def mock_file(filename, *args, **kwargs):
        if filename == test_file1:
            return mock_open(read_data=file_content1)(*args, **kwargs)
        elif filename == test_file2:
            return mock_open(read_data=file_content2)(*args, **kwargs)
        raise FileNotFoundError(f"Unexpected file open: {filename}")

    with patch("utils.hashing.hashing.open", side_effect=mock_file) as mock_open_call:
        with patch("os.path.getsize") as mock_getsize:
            mock_getsize.side_effect = lambda x: len(file_content1)  # Same size
            assert (
                HashingUtils.compare_hashes(test_file1, test_file2, ComparisonMode.FULL)
                is True
            )
            # Ensure get_hash was called (implicitly via compare_hashes in FULL mode)
            # Check that open was called for hashing
            assert (
                mock_open_call.call_count >= 2
            )  # At least once for size check (implicitly), once per get_hash


def test_compare_hashes_full_mode_different():
    # Test with different files using FULL comparison mode
    test_file1 = "test1.txt"
    file_content1 = b"Content A"
    test_file2 = "test2.txt"
    file_content2 = b"Content B"  # Different content

    def mock_file(filename, *args, **kwargs):
        if filename == test_file1:
            return mock_open(read_data=file_content1)(*args, **kwargs)
        elif filename == test_file2:
            return mock_open(read_data=file_content2)(*args, **kwargs)
        raise FileNotFoundError(f"Unexpected file open: {filename}")

    with patch("utils.hashing.hashing.open", side_effect=mock_file) as mock_open_call:
        with patch("os.path.getsize") as mock_getsize:
            mock_getsize.side_effect = lambda x: len(
                file_content1
            )  # Same size, different content
            assert (
                HashingUtils.compare_hashes(test_file1, test_file2, ComparisonMode.FULL)
                is False
            )
            # Ensure get_hash was called
            assert mock_open_call.call_count >= 2


def test_compare_hashes_file1_not_found():
    # Test when file1 does not exist
    test_file1 = "non_existent1.txt"
    test_file2 = "test2.txt"  # Assume this exists for the test setup

    # Mock os.path.exists to simulate file1 not existing
    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = lambda path: path == test_file2

        # Expect FileNotFoundError because compare_hashes should check existence first
        with pytest.raises(FileNotFoundError, match=f"File not found: {test_file1}"):
            # We don't need to mock getsize or open if exists is checked first
            HashingUtils.compare_hashes(test_file1, test_file2, ComparisonMode.PARTIAL)


def test_compare_hashes_file2_not_found():
    # Test when file2 does not exist
    test_file1 = "test1.txt"  # Assume this exists for the test setup
    test_file2 = "non_existent2.txt"

    # Mock os.path.exists to simulate file2 not existing
    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = lambda path: path == test_file1

        # Mock os.path.getsize for the initial size check of the existing file1
        # This is needed because the function checks size before checking file2 existence in some paths
        with patch("os.path.getsize", return_value=100):
            # Expect FileNotFoundError because compare_hashes should check existence of file2
            with pytest.raises(
                FileNotFoundError, match=f"File not found: {test_file2}"
            ):
                # Use PARTIAL mode for consistency, though the error should raise before mode matters
                HashingUtils.compare_hashes(
                    test_file1, test_file2, ComparisonMode.PARTIAL
                )


def test_compare_hashes_partial_io_error_read():
    # Test IOError during partial read
    test_file1 = "test1.txt"
    test_file2 = "test2.txt"
    file_content = b"Long enough content for partial check" * 100
    partial_size = 4096

    mock_file1 = mock_open(read_data=file_content)
    mock_file2 = mock_open(read_data=file_content)

    # Simulate IOError on second read of file1
    original_read1 = mock_file1().read

    def faulty_read1(*args, **kwargs):
        if faulty_read1.call_count == 1:
            faulty_read1.call_count += 1
            return original_read1(*args, **kwargs)  # First read ok
        raise IOError("Cannot read file1")

    faulty_read1.call_count = 0
    mock_file1().read = faulty_read1

    def mock_file_opener(filename, *args, **kwargs):
        if filename == test_file1:
            return mock_file1()
        elif filename == test_file2:
            return mock_file2()
        raise FileNotFoundError(f"Unexpected file open: {filename}")

    with patch("os.path.getsize", return_value=len(file_content)):
        with patch("utils.hashing.hashing.open", side_effect=mock_file_opener):
            with pytest.raises(
                IOError, match=f"Error reading files {test_file1} or {test_file2}"
            ):
                HashingUtils.compare_hashes(
                    test_file1,
                    test_file2,
                    ComparisonMode.PARTIAL,
                    partial_check_size=partial_size,
                )


def test_compare_hashes_partial_different_end_chunk():
    # Test PARTIAL mode where start chunks match but end chunks differ
    test_file1 = "test1.txt"
    test_file2 = "test2.txt"
    # Ensure content is longer than partial_check_size * 2
    common_start = b"START" * 1000
    end1 = b"END1" * 1000
    end2 = b"END2" * 1000
    middle = b"MIDDLE" * 500
    file_content1 = common_start + middle + end1
    file_content2 = common_start + middle + end2
    partial_size = 4096  # Default size

    assert len(file_content1) == len(file_content2)  # Sizes must match
    assert len(file_content1) > partial_size * 2  # Ensure seek works correctly

    # More robust mock for seek and read
    mock_f1 = mock_open(read_data=file_content1)()
    mock_f2 = mock_open(read_data=file_content2)()

    # Keep track of file pointers
    pointers = {test_file1: 0, test_file2: 0}
    contents = {test_file1: file_content1, test_file2: file_content2}

    def custom_seek(filename, offset, whence=os.SEEK_SET):
        content_len = len(contents[filename])
        if whence == os.SEEK_SET:
            pointers[filename] = offset
        elif whence == os.SEEK_CUR:
            pointers[filename] += offset
        elif whence == os.SEEK_END:
            pointers[filename] = content_len + offset
        else:
            raise ValueError("Invalid whence value")
        # Clamp pointer
        pointers[filename] = max(0, min(content_len, pointers[filename]))
        return pointers[filename]

    def custom_read(filename, size=-1):
        content = contents[filename]
        current_pos = pointers[filename]
        content_len = len(content)

        if size == -1:
            read_size = content_len - current_pos
        else:
            read_size = min(size, content_len - current_pos)

        data = content[current_pos : current_pos + read_size]
        pointers[filename] += read_size
        return data

    # Patch the methods on the mock objects
    mock_f1.seek = lambda offset, whence=os.SEEK_SET: custom_seek(
        test_file1, offset, whence
    )
    mock_f1.read = lambda size=-1: custom_read(test_file1, size)
    mock_f2.seek = lambda offset, whence=os.SEEK_SET: custom_seek(
        test_file2, offset, whence
    )
    mock_f2.read = lambda size=-1: custom_read(test_file2, size)

    def advanced_mock_opener(filename, *args, **kwargs):
        pointers[filename] = 0  # Reset pointer on open
        if filename == test_file1:
            return mock_f1
        elif filename == test_file2:
            return mock_f2
        raise FileNotFoundError(f"Unexpected file open: {filename}")

    with patch("os.path.getsize", return_value=len(file_content1)):
        # Patch open within the hashing module's scope
        with patch("utils.hashing.hashing.open", side_effect=advanced_mock_opener):
            result = HashingUtils.compare_hashes(
                test_file1,
                test_file2,
                ComparisonMode.PARTIAL,
                partial_check_size=partial_size,
            )
            assert result is False  # End chunks should differ
