import os
import json

from CTRegisterMicroserviceFlask import request_to_microservice


def query_micoservice(sql):
    local_env = os.getenv('ENVIRONMENT')
    if local_env == 'dev':

        # can't seem to get GET requests working locally
        # this will be much easier in proudction - should just be a GET
        config = {
            'uri': '/query/3267be92-733f-45e4-bf81-be5a2b33112c?sql={}'.format(sql),
            'method': 'POST',
            'body': {"dataset": {"tableName": "index_3267be92733f45e4bf81be5a2b33112c_1528900401608"}}
        }

    else:
        dataset_id = os.getenv('FIRES_DATASET_ID')
        config = {
            'uri': '/query/{}?sql={}'.format(dataset_id, sql),
            'method': 'GET',
        }

    return request_to_microservice(config)


def load_valid_poly_iso():
    with open('fireSummary/data/gadm28.json') as thedata:
        return json.load(thedata)
