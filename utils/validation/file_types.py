from enum import Enum


class FileType(str, Enum):
    """Enum for file types."""

    IMAGE = "image"
    VIDEO = "video"

    def __str__(self) -> str:
        return self.value
