import os
from CTRegisterMicroserviceFlask import request_to_microservice


def query_micoservice(sql):
    local_env = os.getenv('ENVIRONMENT')
    if local_env == 'dev':

        # can't seem to get GET requests working locally
        # this will be much easier in proudction - should just be a GET
        config = {
            'uri': '/query/d1aed395-3918-4b0a-b025-684ef9863403?sql={}'.format(sql),
            'method': 'POST',
            'body': {"dataset": {"tableName": "index_d1aed39539184b0ab025684ef9863403_1528744869921"}}
        }

    else:
        dataset_id = os.getenv('FIRES_DATASET_ID')
        config = {
            'uri': '/query/{}?sql={}'.format(dataset_id, sql),
            'method': 'GET',
        }

    return request_to_microservice(config)
