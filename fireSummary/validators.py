"""VALIDATORS"""

import datetime

from flask import jsonify, Blueprint, request
from functools import wraps
from fireSummary.routes.api import error
import logging
from utils import util


def validate_args_fires(func):

    """Validate user arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        # validate iso/adm1/adm2 combo
        iso = request.view_args.get('iso_code', None)
        adm1 = request.view_args.get('adm1_code', None)
        adm2 = request.view_args.get('adm2_code', None)

        input_combo = [iso, adm1, adm2]

        # get rid of None's
        input_combo = [x for x in input_combo if x is not None]

        # create list of valid admin combos, based on input combo
        input_len = len(input_combo) + 1

        # read in all possible poly/iso/adm1/adm2 combos
        poly_iso_adm1_adm2_combos = util.load_valid_poly_iso()
        iso_adm1_adm2_combos = [x[1:input_len] for x in poly_iso_adm1_adm2_combos]

        if len(input_combo) > 1 and input_combo[0] == 'global':
            return error(status=400, detail="if requesting globally summarized statistics, you cannot choose "
                                            "additional administrative units.")

        if input_combo[0] != 'global' and input_combo not in iso_adm1_adm2_combos:
            return error(status=400, detail='That combination of admin units (ISO, adm1, adm2) does not exist. Please'
                                            ' consult the GADM dataset (https://gadm.org/) to determine '
                                            'a valid combination')

        # validate polyname
        polyname = request.view_args['polyname']

        # get valid polynames from pre-calc stats
        valid_polyname_list = [x[0] for x in poly_iso_adm1_adm2_combos]

        # group polynames
        valid_polyname_list = list(set(valid_polyname_list))

        # swap gadm for admin
        valid_polyname_list = ['admin' if 'gadm' in x else x for x in valid_polyname_list]

        if polyname.lower() not in valid_polyname_list:
            return error(status=400, detail='For this batch service, polyname must one of: {}'
                         .format(', '.join(valid_polyname_list)))

        # validate firetype
        fire_type = request.args.get('fire_type')
        if fire_type:
            valid_fire_list = ['viirs', 'modis', 'all']
            if fire_type.lower() not in valid_fire_list:
                return error(status=400, detail='For this batch service, fire_type must one of {}'.format(', '.join(valid_fire_list)))

        aggregate_error = validate_aggregate(iso)
        if aggregate_error:
            return aggregate_error

        period_error = validate_period()
        if period_error:
            return period_error

        return func(*args, **kwargs)

    return wrapper


def validate_args_glad(func):
    """Validate user arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        # validate iso/adm1/adm2 combo
        iso = request.view_args.get('iso_code', None)
        adm1 = request.view_args.get('adm1_code', None)
        adm2 = request.view_args.get('adm2_code', None)

        input_combo = [iso, adm1, adm2]

        # get rid of None's
        input_combo = [x for x in input_combo if x is not None]

        # create list of valid admin combos, based on input combo
        input_len = len(input_combo) + 1

        # read in all possible poly/iso/adm1/adm2 combos
        poly_iso_adm1_adm2_combos = util.load_valid_poly_iso()
        iso_adm1_adm2_combos = [x[1:input_len] for x in poly_iso_adm1_adm2_combos]

        if len(input_combo) > 1 and input_combo[0] == 'global':
            return error(status=400, detail="if requesting globally summarized statistics, you cannot choose "
                                            "additional administrative units.")

        if input_combo[0] != 'global' and input_combo not in iso_adm1_adm2_combos:
            return error(status=400, detail='That combination of admin units (ISO, adm1, adm2) does not exist. Please'
                                            ' consult the GADM dataset (https://gadm.org/) to determine '
                                            'a valid combination')

        aggregate_error = validate_aggregate(iso)
        if aggregate_error:
            return aggregate_error

        period_error = validate_period()
        if period_error:
            return period_error

        return func(*args, **kwargs)

    return wrapper


def validate_period():

    # validate period
    today = datetime.datetime.now()
    period = request.args.get('period', None)
    minYear = 2001
    if period:

        if len(period.split(',')) < 2:
            return error(status=400, detail="Period needs 2 arguments")

        else:
            if '"' in period or "'" in period:
                return error(status=400, detail="Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

            period_from = period.split(',')[0]
            period_to = period.split(',')[1]

            try:
                period_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
                period_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')
            except ValueError:
                return error(status=400, detail="Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

            if period_from.year < minYear:
                return error(status=400, detail="Start date can't be earlier than {}-01-01".format(minYear))

            if period_to.year > today.year:
                return error(status=400, detail="End year can't be later than {}".format(today.year))

            if period_from > period_to:
                return error(status=400, detail='Start date must be less than end date')

            else:
                return None


def validate_aggregate(iso):
    # validate aggregate
    agg_by = request.args.get('aggregate_by')
    agg_values = request.args.get('aggregate_values')

    agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'adm2']

    if iso == 'global':
        agg_list = [x for x in agg_list if x not in ['adm2']]
        agg_list.append('iso')

    if agg_values:
        if agg_values.lower() not in ['true', 'false']:
            return error(status=400, detail="aggregate_values parameter "
                                            "must be either true or false")

        agg_values = eval(agg_values.title())

    # validate aggregating with global summary
    if agg_values and agg_by:

        if agg_by.lower() not in agg_list:
            return error(status=400,
                         detail="aggregate_by must be specified as one of: {} ".format(", ".join(agg_list)))

        if agg_by and not agg_values:
            return error(status=400, detail="aggregate_values parameter must be "
                                            "true in order to aggregate data")

        if agg_values and not agg_by:
            return error(status=400,
                         detail="if aggregate_values is TRUE, aggregate_by parameter must be specified "
                            "as one of: {}".format(", ".join(agg_list)))
