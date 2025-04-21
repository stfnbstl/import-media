import hashlib
import os

from utils.validation.comparison_mode import ComparisonMode


class HashingUtils:
    """A utility class for hashing operations on files."""

    @staticmethod
    def get_hash(file: str, buffer_size: int = 4096) -> str:
        """Calculates the SHA256 hash of a file.

        Args:
            file (str): The path to the file to hash.
            buffer_size (int): The buffer size to use when reading the file. Defaults to 4096.

        Returns:
            str: The SHA256 hash of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be read.
        """
        sha256 = hashlib.sha256()
        try:
            with open(file, "rb") as f:
                while True:
                    data = f.read(buffer_size)
                    if not data:
                        break
                    sha256.update(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file}")
        except IOError as e:
            raise IOError(f"Error reading file {file}: {e}")
        return sha256.hexdigest()

    @staticmethod
    def compare_hashes(
        file1: str,
        file2: str,
        comparison_mode: ComparisonMode,
        buffer_size: int = 4096,
        partial_check_size: int = 4096,
    ) -> bool:
        """Compares two files efficiently to determine if they are identical based on the specified mode.

        Performs checks in order of increasing cost:
        1. File size check (always performed).
        2. Comparison of the first and last `partial_check_size` bytes (if ComparisonMode.PARTIAL).
        3. Full SHA256 hash comparison (if ComparisonMode.FULL).

        Args:
            file1 (str): The path to the first file.
            file2 (str): The path to the second file.
            comparison_mode (ComparisonMode): The mode to use for comparison (PARTIAL or FULL).
            buffer_size (int): The buffer size for full hashing (used in FULL mode). Defaults to 4096.
            partial_check_size (int): The size of the head/tail chunks to compare (used in PARTIAL mode). Defaults to 4096.

        Returns:
            bool: True if the files are considered identical based on the comparison mode, False otherwise.

        Raises:
            FileNotFoundError: If either file does not exist.
            IOError: If either file cannot be read.
        """
        try:
            # 1. Check file sizes first
            # This is the fastest check and can quickly rule out non-identical files
            # If the sizes are different, the files are not identical
            # If the sizes are equal, we proceed to the next checks
            size1 = os.path.getsize(file1)
            size2 = os.path.getsize(file2)
            if size1 != size2:
                return False

            match comparison_mode:
                case ComparisonMode.PARTIAL:
                    # Compare beginning and end chunks
                    with open(file1, "rb") as f1, open(file2, "rb") as f2:
                        # Compare beginning chunk
                        if f1.read(partial_check_size) != f2.read(partial_check_size):
                            return False

                        # Compare end chunk
                        f1.seek(-partial_check_size, os.SEEK_END)
                        f2.seek(-partial_check_size, os.SEEK_END)
                        if f1.read(partial_check_size) != f2.read(partial_check_size):
                            return False

                        # If the sizes are equal and the beginning and end chunks match, we can assume they are identical
                        return True
                case ComparisonMode.FULL:
                    # If sizes match and mode is FULL compare full hashes (most reliable)
                    hash1 = HashingUtils.get_hash(file1, buffer_size)
                    hash2 = HashingUtils.get_hash(file2, buffer_size)
                    return hash1 == hash2

        except FileNotFoundError as e:
            if not os.path.exists(file1):
                raise FileNotFoundError(f"File not found: {file1}") from e
            if not os.path.exists(file2):
                raise FileNotFoundError(f"File not found: {file2}") from e
            raise e
        except IOError as e:
            raise IOError(f"Error reading files {file1} or {file2}: {e}") from e
