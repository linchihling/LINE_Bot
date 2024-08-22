import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Function to set up a logger with RotatingFileHandler and StreamHandler."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # RotatingFileHandler
    fh = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=5)
    fh.setLevel(level)

    # StreamHandler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

