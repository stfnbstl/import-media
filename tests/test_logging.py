import pytest
from utils.logs.logging_utils import LoggingUtils
import logging


def test_get_base_logger():
    # Test with valid parameters
    logger = LoggingUtils.get_base_logger(logging.INFO, "%(message)s", "test_logger")
    assert logger.name == "test_logger"
    assert logger.level == 20  # INFO level is 20


def test_get_base_logger_invalid_level():
    # Test with invalid loglevel
    with pytest.raises(ValueError):
        LoggingUtils.get_base_logger("invalid_level")


def test_get_base_logger_empty_format():
    # Test with empty log_format
    with pytest.raises(ValueError):
        LoggingUtils.get_base_logger(logging.INFO, "")
