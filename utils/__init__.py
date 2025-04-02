from utils.hashing.hashing import HashingUtils
from utils.exif.exif import ExifUtils
from utils.logs.logging_utils import LoggingUtils

# Create convenience functions that map to class methods
get_hash = HashingUtils.get_hash
compare_hashes = HashingUtils.compare_hashes
get_date_taken = ExifUtils.get_date_taken
get_base_logger = LoggingUtils.get_base_logger

__all__ = [
    "get_base_logger",
    "get_date_taken",
    "compare_hashes",
    "get_hash",
    "HashingUtils",
    "ExifUtils",
    "LoggingUtils",
]
