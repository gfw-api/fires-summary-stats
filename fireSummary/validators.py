"""VALIDATORS"""
import datetime
import logging
from functools import wraps

from flask import jsonify, Blueprint, request

from fireSummary.errors import Error
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
            raise Error("if requesting globally summarized statistics, you cannot choose "
                        "additional administrative units.")

        if input_combo[0] != 'global' and input_combo not in iso_adm1_adm2_combos:
            raise Error('That combination of admin units (ISO, adm1, adm2) does not exist. Please'
                        ' consult the GADM dataset (https://gadm.org/) to determine a valid combination')

        # validate polyname
        polyname = request.view_args['polyname']

        # get valid polynames from pre-calc stats
        valid_polyname_list = [x[0] for x in poly_iso_adm1_adm2_combos]

        # group polynames
        valid_polyname_list = list(set(valid_polyname_list))

        # swap gadm for admin
        valid_polyname_list = ['admin' if 'gadm' in x else x for x in valid_polyname_list]

        if polyname.lower() not in valid_polyname_list:
            raise Error('For this batch service, polyname must one of: {}'
                         .format(', '.join(valid_polyname_list)))

        # validate firetype
        fire_type = request.args.get('fire_type')
        if fire_type:
            valid_fire_list = ['viirs', 'modis', 'all']
            if fire_type.lower() not in valid_fire_list:
                raise Error('For this batch service, fire_type must one of {}'.format(', '.join(valid_fire_list)))

        validate_aggregate(iso)

        validate_period(2001)
        
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
            raise Error("if requesting globally summarized statistics, you cannot choose "
                        "additional administrative units.")

        if input_combo[0] != 'global' and input_combo not in iso_adm1_adm2_combos:
            raise Error('That combination of admin units (ISO, adm1, adm2) does not exist. Please'
                        ' consult the GADM dataset (https://gadm.org/) to determine a valid combination')

        validate_aggregate(iso)

        validate_period(2015)

        return func(*args, **kwargs)

    return wrapper


def validate_period(minYear):

    # validate period
    today = datetime.datetime.now()
    period = request.args.get('period', None)
    if period:

        if len(period.split(',')) < 2:
            raise Error("Period needs 2 arguments")

        else:
            if '"' in period or "'" in period:
                raise Error("Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

            period_from = period.split(',')[0]
            period_to = period.split(',')[1]

            try:
                period_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
                period_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')
            except ValueError:
                raise Error("Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

            if period_from.year < minYear:
                raise Error("Start date can't be earlier than {}-01-01".format(minYear))

            if period_to.year > today.year:
                raise Error("End year can't be later than {}".format(today.year))

            if period_from > period_to:
                raise Error('Start date must be less than end date')

            else:
                return None


def validate_aggregate(iso):
    # validate aggregate
    agg_values = request.args.get('aggregate_values')
    agg_by = request.args.get('aggregate_by')
    agg_admin = request.args.get('aggregate_admin')
    agg_time = request.args.get('aggregate_time')

    valid_agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'adm2']

    if iso == 'global':
        valid_agg_list = [x for x in valid_agg_list if x not in ['adm2']]
        valid_agg_list.append('iso')

    if agg_values:
        if agg_values.lower() not in ['true', 'false']:
            raise Error("aggregate_values parameter must be either true or false")

        # convert from string to boolean
        agg_values = eval(agg_values.title())

    # validate aggregating with global summary
    if (agg_by and agg_admin) or (agg_by and agg_time):
        raise Error("can't combine an aggregate_by with any other aggregation. "
                    "If you'd like to use two aggregations, use aggregate_time and aggregate_admin")

    input_agg_list = [x for x in [agg_by, agg_admin, agg_time] if x is not None]

    if input_agg_list and agg_values:
        improper_agg_list = [x for x in input_agg_list if x not in valid_agg_list]

        if improper_agg_list:
            raise Error("aggregate_by or aggregate_time or aggregate_admin must be "
                        "specified as one of: {} ".format(", ".join(valid_agg_list)))

    elif input_agg_list and not agg_values:
            raise Error("aggregate_values parameter must be true in order to aggregate data")

    elif agg_values and not input_agg_list:
            raise Error("if aggregate_values is True, aggregate_by OR aggregate_admin OR aggregate_time parameters" 
                        "must be specified as one of {}".format(", ".join(valid_agg_list)))

