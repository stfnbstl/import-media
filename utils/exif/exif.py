from PIL import Image
from datetime import datetime
from typing import Optional
import logging


class ExifUtils:
    """
    Utilities for working with EXIF metadata in images.

    This class provides methods to extract and manipulate EXIF data
    from image files.

    Example:
        date_taken = ExifUtils.get_date_taken('path/to/image.jpg')
    """

    # EXIF tags as named constants
    EXIF_DATETIME_ORIGINAL = 36867
    EXIF_DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"

    @staticmethod
    def get_date_taken(path: str) -> Optional[datetime]:
        """
        Get the date the image was taken from EXIF metadata.

        Args:
            path: Path to the image file

        Returns:
            datetime object representing when the photo was taken, or None if
            the information is not available or an error occurred

        Note:
            If an exception occurs during EXIF data extraction (e.g., file not found,
            invalid format), the error will be logged and the method will return None.
        """
        try:
            with Image.open(path) as img:
                exif_data = img._getexif()
                if exif_data and ExifUtils.EXIF_DATETIME_ORIGINAL in exif_data:
                    return datetime.strptime(
                        exif_data[ExifUtils.EXIF_DATETIME_ORIGINAL],
                        ExifUtils.EXIF_DATETIME_FORMAT,
                    )

            # No date found in EXIF data
            return None
        except Exception as e:
            logging.error(f"Error extracting EXIF data from {path}: {str(e)}")
            return None
