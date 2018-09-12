import os
import json

from CTRegisterMicroserviceFlask import request_to_microservice

from fireSummary.errors import Error


def query_microservice(sql, analysis_type):

    if analysis_type == 'glad':
        dataset_id = os.getenv('GLAD_DATASET_ID')
    elif analysis_type == 'fires':
        dataset_id = os.getenv('FIRES_DATASET_ID')
    else:
        raise Error('unknown analyis type: {}'.format(analysis_type))

    config = {
        'uri': '/query/{}?sql={}'.format(dataset_id, sql),
        'method': 'GET',
    }

    response = request_to_microservice(config)

    if response.get('errors'):
        raise Error(**response['errors'][0])

    else:
        return response


def load_valid_poly_iso():
    with open('fireSummary/data/gadm28.json') as thedata:
        return json.load(thedata)

