"""API ROUTER"""

import logging
import os
import time

from flask import jsonify, Blueprint, request
from ps.routes.api import error
from ps.middleware import set_something
from ps.serializers import serialize_response
import json
from CTRegisterMicroserviceFlask import request_to_microservice
import requests

from ps.validators import validate_fires_period, validate_agg, validate_firetype
from ps.services import SummaryService, QueryConstructorService
from ps.serializers import serialize_response

fires_endpoints = Blueprint('fires_endpoints', __name__)


def summarize_data(polyname, iso_code, adm1_code=None, adm2_code=None):

    if polyname == 'admin':
        polyname = 'gadm28'

    # construct sql query
    sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code, adm1_code, adm2_code)
    logging.info("SQL REQUEST: {}".format(sql))

    local_env = os.getenv('ENVIRONMENT')
    if local_env == 'dev':

        # can't seem to get GET requests working locally
        # this will be much easier in proudction - should just be a GET
        config = {
          'uri': '/query/d48d2995-9bfe-46d1-bb13-ec1aa3ebdef6?sql={}'.format(sql),
          'method': 'POST',
          'body': {"dataset": {"tableName": "index_0ff00a71a6cd4313bc00c353f51318d1_1528308846698"}}
        }

    else:
        dataset_id = os.getenv('FIRES_DATASET_ID')
        config = {
          'uri': '/query/{}?sql={}'.format(dataset_id, sql),
          'method': 'GET',
         }

    data = request_to_microservice(config)
        
    # aggregate data
    agg_data = SummaryService.create_time_table(data, polyname, request, iso_code)

    #serialize data
    serialized_data = serialize_response(request, agg_data, polyname)

    return serialized_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_fires_period
@validate_agg
@validate_firetype
def fires_polyname_iso(polyname, iso_code, adm1_code=None, adm2_code=None, fire_type=None):

    logging.info('[ROUTER]: Running aoi level fires analysis')

    return jsonify(summarize_data(polyname, iso_code, adm1_code, adm2_code))
