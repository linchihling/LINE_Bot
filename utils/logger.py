import logging
import logging.config
import yaml


def setup_logger(name):
    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    return logging.getLogger(name)

# # Elasticsearch
# from elasticsearch import Elasticsearch
# es = Elasticsearch(
#     hosts=["http://elastic.tunghosteel.com:9200"],  
#     http_auth=("elastic", "ClientS00")
# )
# response = es.index(index=project_name, document=doc)



