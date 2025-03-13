import logging
import logging.config
import yaml


class ProjectLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, {
            **kwargs,
            "extra": {"project": self.extra.get("project", "unknown")},
        }


def setup_logger(name, project_name):
    with open("logging.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    logger = logging.getLogger(name)
    return ProjectLoggerAdapter(logger, {"project": project_name})
