import json
import logging
import logging.handlers
from pathlib import Path


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        })


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    return logger
