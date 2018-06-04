"""API ROUTER"""

import logging

from flask import jsonify, Blueprint, request
from ps.routes.api import error
from ps.validators import validate_greeting
from ps.middleware import set_something
from ps.serializers import serialize_response
import json
import CTRegisterMicroserviceFlask
import requests
import datetime
from ps.validators import validate_fires_period, validate_agg
from ps.services import SummaryService

fires_endpoints = Blueprint('fires_endpoints', __name__)

# add period
# aggregate by iso, adm1, adm2, polyname,


def summarize_data(polyname, iso_code, adm1_code=None, adm2_code=None):

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    # get parameters from query string
    period = request.args.get('period', '2015-01-01,{}'.format(today))
    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', None)

    dates = period.split(',')
    start_date = dates[0].replace('-', '/')
    end_date = dates[1].replace('-', '/')

    url = "https://production-api.globalforestwatch.org/query/4145f642-5455-4414-b214-58ad39b83e1e?sql=" \
          "SELECT sum(fire_count) FROM data WHERE polyname = '{0}' and iso = '{1}' and (fire_date >= '{2}'" \
          " and fire_date <= '{3}')".format(polyname, iso_code, start_date, end_date)

    # aggregate admin....query IDN states, where iso = IDN, group by adm1, period 2001-10-10, 2010-01-01, return top 5
    if agg_values:
        url = "https://production-api.globalforestwatch.org/query/4145f642-5455-4414-b214-58ad39b83e1e?sql=" \
              "SELECT * FROM data WHERE polyname = '{0}' and iso = '{1}' and (fire_date >= '{2}'" \
              " and fire_date <= '{3}')".format(polyname, iso_code, start_date, end_date)

    if adm1_code:
        url += " and adm1 = {}".format(adm1_code)

    if adm2_code:
        url += " and adm2 = {}".format(adm2_code)

    logging.info("REQUESTED URL: {}".format(url))

    r = requests.get(url)
    data = r.json()

    agg_data = SummaryService.create_time_table('glad', data, agg_by)

    return agg_data


@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>', methods=['GET'])
@fires_endpoints.route('/summary-stats/<polyname>/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
@validate_fires_period
@validate_agg
def fires_polyname_iso(polyname, iso_code, adm1_code=None, adm2_code=None):
    """summarize fires by gadm geom"""
    logging.info('[ROUTER]: Running aoi level fires analysis')

    if polyname == 'admin':
        polyname = 'gadm28'

    # validate date to be in format YYYY-mm-dd, change it to YYYY/mm/dd for elastic to recognize, then run query
    # analyze layer
    return jsonify(summarize_data(polyname, iso_code, adm1_code, adm2_code))
