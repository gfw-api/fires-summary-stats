"""API ROUTER"""

import logging

from flask import jsonify, Blueprint, request

from fireSummary.utils import util
from fireSummary.validators import validate_args_fires, validate_args_glad
from fireSummary.middleware import valid_input_boundaries
from fireSummary.services import SummaryService, QueryConstructorService
from fireSummary.serializers import serialize_response
from fireSummary.errors import Error

fires_endpoints = Blueprint('fires_endpoints', __name__)
glad_endpoints = Blueprint('glad_endpoints', __name__)


@valid_input_boundaries
def summarize_data(dataset_name, params, is_valid_combo):

    # we've already validated that the input iso/adm1/adm2 exists, and the
    # polyname (if applicable) exists. Now time to see if the full combo
    # (like - wdpa/BRA/1/1) exists in the world
    if is_valid_combo:
        if params['polyname'] == 'admin':
            params['polyname'] = 'gadm28'

        # construct sql query
        sql = QueryConstructorService.format_dataset_query(dataset_name, params)
        logging.info("\nSQL REQUEST: {}".format(sql))

        # get response from microservice
        data = util.query_microservice(
            sql, dataset_name, request.headers.get("x-api-key")
        )

        # now that actual querying is done, replace gadm28 with admin
        if params['polyname'] == 'gadm28':
            params['polyname'] = 'admin'

        # aggregate data
        agg_data = SummaryService.create_time_table(dataset_name, data, params)

    # if there's no wdpa/BRA/1/1 (essentially no possibility for alerts in
    # this combination because it doesn't exist), return `null`
    else:
        agg_data = None

    # serialize data
    serialized_data = serialize_response(dataset_name, agg_data, params)

    return serialized_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_args_fires
def fires_polyname_iso(params):
    return jsonify(summarize_data('fires', params))


@glad_endpoints.route('/summary-stats/admin/<iso_code>', methods=['GET'])
@glad_endpoints.route('/summary-stats/admin/<iso_code>/<adm1_code>', methods=['GET'])
@glad_endpoints.route('/summary-stats/admin/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_args_glad
def glad_polyname_iso(params):
    return jsonify(summarize_data('glad', params))


@glad_endpoints.errorhandler(Error)
def handle_error(error):
    return error.serialize


@fires_endpoints.errorhandler(Error)
def handle_error(error):
    return error.serialize

