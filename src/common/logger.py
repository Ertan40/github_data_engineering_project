"""
logging.getLogger(name) creates or retrieves a named logger.
setLevel(logging.INFO) means INFO and higher levels will be recorded.
StreamHandler() sends messages to the console.
Formatter() defines the structure of each log message.
if not logger.handlers prevents adding duplicate handlers when the same logger is retrieved again.
"""
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
