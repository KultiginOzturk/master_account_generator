"""Lightweight structured logger wrapper.

Sets up a basic logging configuration (if none exists) and exposes
`info`, `warning`, and `error` methods that accept extra key/value data.
"""
import logging
from typing import Any, Dict


class DQLogger:
    def __init__(self, name: str = __name__):
        """A wrapper around Python logging with Cloud Logging defaults."""
        root = logging.getLogger()
        if not root.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
            )
        self._std_logger = logging.getLogger(name)

    def _format_message(self, message: str, extra: Dict[str, Any]) -> str:
        return f"{message} {extra}" if extra else message

    def info(self, message: str, **extra: Any) -> None:
        self._std_logger.info(self._format_message(message, extra))

    def warning(self, message: str, **extra: Any) -> None:
        self._std_logger.warning(self._format_message(message, extra))

    def error(self, message: str, **extra: Any) -> None:
        self._std_logger.error(self._format_message(message, extra))
