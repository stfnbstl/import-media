from enum import Enum


class Strategy(str, Enum):
    """
    Strategy to use when importing data.
    """

    REPLACE = "replace"
    ONLYNEW = "onlynew"
    RENAME = "rename"
