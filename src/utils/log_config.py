import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:
    """
    Initializes the logging system for the application.

    This function performs the following actions:
    1. Creates the log directory if it does not exist.
    2. Configures the root logger with a RotatingFileHandler (for detailed persistence) and a StreamHandler (for concise console output).

    This should be called exactly once at the application startup entry point.
    """
    Path("logs").mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG) 
    root_logger.handlers = []

    file_handler = RotatingFileHandler(
        Path("logs") / "app.log", 
        maxBytes=5_000_000,
        backupCount=3, 
        encoding="utf-8"
    )
    file_formatter = logging.Formatter("%(filename)s:%(lineno)d - %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter("%(levelname)s: [%(name)s] %(message)s")
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.DEBUG)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

def get_logger(module_name: str) -> logging.Logger:
    """
    Retrieves a logger instance identified by the given module name.

    This function returns a standard logger that propagates messages to the
    root logger configured in `setup_logging`. It is safe to call this function
    at the top level of any module (import time), as it does not perform any
    I/O operations or handler configurations directly.

    Args:
        module_name (str): The name of the module requesting the logger.

    Returns:
        logging.Logger: The configured logger instance.
    """
    return logging.getLogger(module_name)