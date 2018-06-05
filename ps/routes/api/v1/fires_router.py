"""API ROUTER"""

import logging
import time

from flask import jsonify, Blueprint, request
from ps.routes.api import error
from ps.middleware import set_something
from ps.serializers import serialize_response
import json
import CTRegisterMicroserviceFlask
import requests

from ps.validators import validate_fires_period, validate_agg, validate_firetype
from ps.services import SummaryService, QueryConstructorService

fires_endpoints = Blueprint('fires_endpoints', __name__)


def summarize_data(polyname, iso_code, adm1_code=None, adm2_code=None):

    if polyname == 'admin':
        polyname = 'gadm28'

    # construct sql query
    sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code, adm1_code, adm2_code)
    logging.info("SQL REQUEST: {}".format(sql))

    api_url = "https://production-api.globalforestwatch.org/query/4145f642-5455-4414-b214-58ad39b83e1e?sql={}"

    url = api_url.format(sql)

    # send request to fires api
    fstart = time.time()
    r = requests.get(url)
    data = r.json()
    logging.info("TIME FOR API: {}".format(time.time() - fstart))

    # aggregate data
    pstart = time.time()
    agg_data = SummaryService.create_time_table(data, polyname, request, iso_code)
    logging.info("TIME FOR PANDAS: {}".format(time.time() - pstart))

    return agg_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_fires_period
@validate_agg
@validate_firetype
def fires_polyname_iso(polyname, iso_code, adm1_code=None, adm2_code=None, fire_type=None):

    logging.info('[ROUTER]: Running aoi level fires analysis')

    return jsonify(summarize_data(polyname, iso_code, adm1_code, adm2_code))
