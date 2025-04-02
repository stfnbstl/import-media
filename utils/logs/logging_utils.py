from logging import basicConfig, Logger, getLogger
from rich.logging import RichHandler


class LoggingUtils:
    @staticmethod
    def get_base_logger(
        loglevel: int, log_format: str = "%(message)s", logger_name: str = "rich"
    ) -> Logger:
        """
        Sets up and retrieves a base logger with the specified log level and format.

        The logger is configured to use the Rich library for colorful and enhanced output.

        Args:
            loglevel (int): The desired log level (e.g., logging.DEBUG, logging.INFO).
            log_format (str, optional): The format string for log messages. Defaults to "%(message)s".
            logger_name (str, optional): Name for the logger. Defaults to "rich".

        Returns:
            Logger: A configured logger instance.

        Raises:
            ValueError: If the provided loglevel or log_format is invalid.
        """
        if not isinstance(loglevel, int):
            raise ValueError("Log level must be an integer")
        if not log_format:
            raise ValueError("Log format cannot be empty")

        FORMAT = log_format
        basicConfig(
            format=FORMAT, level=loglevel, datefmt="[ %X ]", handlers=[RichHandler()]
        )
        return getLogger(logger_name)
