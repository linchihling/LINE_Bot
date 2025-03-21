import logging
import logging.config
import yaml
import logstash

with open("config/config.yaml", "r") as f:
    LOGSTASH = yaml.safe_load(f)["LOGSTASH"]


class ProjectLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, {
            **kwargs,
            "extra": {"project": self.extra.get("project", "unknown")},
        }


def setup_logger(name, project_name):
    with open("config/logging.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    logger = logging.getLogger(name)

    logstash_handler = logstash.TCPLogstashHandler(
        LOGSTASH["HOST"], LOGSTASH["PORT"], version=1
    )
    logger.addHandler(logstash_handler)

    return ProjectLoggerAdapter(logger, {"project": project_name})
