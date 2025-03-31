import logging
import logging.config
import yaml
import logstash
import os

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")
LOGGING_CONFIG_PATH = os.getenv("LOGGING_CONFIG_PATH", "config/logging.yaml")

with open(CONFIG_PATH, "r") as f:
    LOGSTASH = yaml.safe_load(f).get("LOGSTASH", {})


class ProjectLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        project = kwargs.get("extra", {}).get("project", "unknown")
        return msg, {**kwargs, "extra": {"project": project}}


def setup_logger(name):
    try:
        with open(LOGGING_CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    except FileNotFoundError:
        raise Exception(f"Logging config file '{LOGGING_CONFIG_PATH}' not found.")
    except yaml.YAMLError:
        raise Exception(
            f"Error parsing the logging config file '{LOGGING_CONFIG_PATH}'."
        )

    logger = logging.getLogger(name)

    if LOGSTASH:
        try:
            logstash_handler = logstash.TCPLogstashHandler(
                LOGSTASH.get("HOST", "localhost"), LOGSTASH.get("PORT", 5959), version=1
            )
            logger.addHandler(logstash_handler)
        except Exception as e:
            print(f"Failed to configure Logstash handler: {e}")

    return ProjectLoggerAdapter(logger, {})
