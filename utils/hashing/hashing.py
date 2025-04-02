import hashlib


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
    def compare_hashes(file1: str, file2: str, buffer_size: int = 4096) -> bool:
        """Compares the hashes of two files to determine if they are identical.

        Args:
            file1 (str): The path to the first file.
            file2 (str): The path to the second file.
            buffer_size (int): The buffer size to use when reading the file. Defaults to 4096.

        Returns:
            bool: True if the hashes of the two files are the same, False otherwise.

        Raises:
            FileNotFoundError: If either file does not exist.
            IOError: If either file cannot be read.
        """
        return HashingUtils.get_hash(file1, buffer_size) == HashingUtils.get_hash(
            file2, buffer_size
        )
