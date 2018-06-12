"""API ROUTER"""

import logging
import os
import time

from flask import jsonify, Blueprint, request
from fireSummary.utils import util
from fireSummary.routes.api import error
from fireSummary.middleware import set_something
from fireSummary.serializers import serialize_response
import json

import requests

from fireSummary.validators import validate_fires_period, validate_agg, validate_firetype, validate_polyname
from fireSummary.services import SummaryService, QueryConstructorService
from fireSummary.serializers import serialize_response

fires_endpoints = Blueprint('fires_endpoints', __name__)


def summarize_data(polyname, iso_code, adm1_code=None, adm2_code=None):

    if polyname == 'admin':
        polyname = 'gadm28'

    # construct sql query
    sql = QueryConstructorService.format_dataset_query(request, polyname, iso_code, adm1_code, adm2_code)
    logging.info("\nSQL REQUEST: {}".format(sql))

    # get response from microservice
    data = util.query_micoservice(sql)

    # aggregate data
    agg_data = SummaryService.create_time_table(data, polyname, request, iso_code)
    logging.info(agg_data[0])

    # serialize data
    serialized_data = serialize_response(request, agg_data, polyname)

    return serialized_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_fires_period
@validate_agg
@validate_firetype
@validate_polyname
def fires_polyname_iso(polyname, iso_code, adm1_code=None, adm2_code=None, fire_type=None):

    logging.info('[ROUTER]: Running aoi level fires analysis')

    return jsonify(summarize_data(polyname, iso_code, adm1_code, adm2_code))
