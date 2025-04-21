from enum import Enum


class ComparisonMode(str, Enum):
    """Enum for comparison modes."""

    FULL = "full"
    PARTIAL = "partial"
