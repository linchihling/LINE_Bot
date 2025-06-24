import logging
import logging.config
import yaml
import logstash
import os

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")
LOGGING_CONFIG_PATH = os.getenv("LOGGING_CONFIG_PATH", "config/logging.yaml")

_loaded_config = None


def load_config(path=None):
    global _loaded_config
    if _loaded_config is not None:
        return _loaded_config

    path = path or CONFIG_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            _loaded_config = yaml.safe_load(f)
        return _loaded_config
    except FileNotFoundError:
        raise Exception(f"Config file '{path}' not found.")
    except yaml.YAMLError:
        raise Exception(f"Error parsing the config file '{path}'.")


class ProjectLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        project = kwargs.get("extra", {}).get("project", "unknown")
        return msg, {**kwargs, "extra": {"project": project}}


def setup_logger(name):
    config = load_config()
    logstash_config = config.get("LOGSTASH", {})

    try:
        with open(LOGGING_CONFIG_PATH, "r") as f:
            logging_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logging_config)
    except FileNotFoundError:
        raise Exception(f"Logging config file '{LOGGING_CONFIG_PATH}' not found.")
    except yaml.YAMLError:
        raise Exception(
            f"Error parsing the logging config file '{LOGGING_CONFIG_PATH}'."
        )

    logger = logging.getLogger(name)

    if logstash_config:
        try:
            logstash_handler = logstash.TCPLogstashHandler(
                logstash_config.get("HOST", "localhost"),
                logstash_config.get("PORT", 5959),
                version=1,
            )
            logger.addHandler(logstash_handler)
        except Exception as e:
            print(f"Failed to configure Logstash handler: {e}")

    return ProjectLoggerAdapter(logger, {})
