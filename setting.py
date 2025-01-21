import logging
import logging.config
import yaml
import os


def setup_logger(project_name):
    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())

        os.environ["PROJECT_NAME"] = project_name
        logging.config.dictConfig(config)

    return logging.getLogger(project_name)

# # Elasticsearch
# from elasticsearch import Elasticsearch
# es = Elasticsearch(
#     hosts=["http://elastic.tunghosteel.com:9200"],  
#     http_auth=("elastic", "ClientS00")
# )
# response = es.index(index=project_name, document=doc)

# # 確認結果
# print(response)


