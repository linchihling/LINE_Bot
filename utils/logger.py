import logging
import logging.config
import yaml


def setup_logger(name):
    with open("logging.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    return logging.getLogger(name)
