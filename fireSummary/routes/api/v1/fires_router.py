"""API ROUTER"""

import logging

from flask import jsonify, Blueprint, request

from fireSummary.utils import util
from fireSummary.validators import validate_args_fires, validate_args_glad
from fireSummary.middleware import valid_input_boundaries
from fireSummary.services import SummaryService, QueryConstructorService
from fireSummary.serializers import serialize_response

fires_endpoints = Blueprint('fires_endpoints', __name__)
glad_endpoints = Blueprint('glad_endpoints', __name__)


@valid_input_boundaries
def summarize_data(dataset_name, polyname, iso_code, adm1_code=None, adm2_code=None, is_valid_combo=None):

    if is_valid_combo:
        if polyname == 'admin':
            polyname = 'gadm28'

        # construct sql query
        sql = QueryConstructorService.format_dataset_query(dataset_name, request, polyname, iso_code, adm1_code, adm2_code)
        logging.info("\nSQL REQUEST: {}".format(sql))

        # get response from microservice
        data = util.query_micoservice(sql, dataset_name)
        # aggregate data
        # now that actual querying is done, replace gadm28 with admin
        if polyname == 'gadm28':
            polyname = 'admin'

        agg_data = SummaryService.create_time_table(dataset_name, data, polyname, request, iso_code)

    else:
        agg_data = None

    # serialize data
    serialized_data = serialize_response(dataset_name, request, agg_data, polyname)

    return serialized_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_args_fires
def fires_polyname_iso(polyname, iso_code, adm1_code=None, adm2_code=None):
    dataset_name = 'fires'
    return jsonify(summarize_data(dataset_name, polyname, iso_code, adm1_code, adm2_code))


@glad_endpoints.route('/summary-stats/admin/<iso_code>', methods=['GET'])
@glad_endpoints.route('/summary-stats/admin/<iso_code>/<adm1_code>', methods=['GET'])
@glad_endpoints.route('/summary-stats/admin/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_args_glad
def glad_polyname_iso(iso_code, adm1_code=None, adm2_code=None):
    dataset_name = 'glad'
    return jsonify(summarize_data(dataset_name, 'admin', iso_code, adm1_code, adm2_code))
