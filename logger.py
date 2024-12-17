import logging
from logging.handlers import RotatingFileHandler
from pytz import timezone
from datetime import datetime

class TimezoneFormatter(logging.Formatter):
    """Custom formatter to include timezone-aware timestamps."""
    def __init__(self, fmt=None, datefmt=None, tz="Asia/Taipei"):
        super().__init__(fmt, datefmt)
        self.tz = timezone(tz)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Set up a logger with RotatingFileHandler and StreamHandler."""
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level)

    handler_args = {
        "maxBytes": 2_000_000,
        "backupCount": 5
    }

    # Handlers
    fh = RotatingFileHandler(log_file, **handler_args)
    ch = logging.StreamHandler()

    formatter = TimezoneFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
