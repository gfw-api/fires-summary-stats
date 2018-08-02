import os
import json

from CTRegisterMicroserviceFlask import request_to_microservice


def query_micoservice(sql, analysis_type):

    if analysis_type == 'glad':
        dataset_id = os.getenv('GLAD_DATASET_ID')
    elif analysis_type == 'fires':
        dataset_id = os.getenv('FIRES_DATASET_ID')
    else:
        raise ValueError('unknown analyis type: {}'.format(analysis_type))

    config = {
        'uri': '/query/{}?sql={}'.format(dataset_id, sql),
        'method': 'GET',
    }

    return request_to_microservice(config)


def load_valid_poly_iso():
    with open('fireSummary/data/gadm28.json') as thedata:
        return json.load(thedata)
