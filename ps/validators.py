"""VALIDATORS"""

from functools import wraps

from ps.routes.api import error

import datetime
import re

from functools import wraps
from flask import request


def validate_fires_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        error = validate_period(2012)
        if error:
            return error

        return func(*args, **kwargs)
    return wrapper


def validate_period(minYear):
    today = datetime.datetime.now()
    period = request.args.get('period', None)

    if period:
        if len(period.split(',')) < 2:
            return error(status=400, detail="Period needs 2 arguments")

        else:
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


def validate_agg(func):
    """validate aggregate_by argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.method == 'GET':
            agg_by = request.args.get('aggregate_by')
            agg_values = request.args.get('aggregate_values')
        elif request.method == 'POST':
            agg_by = request.get_json().get('aggregate_by', None) if request.get_json() else None
            agg_values = request.get_json().get('aggregate_values', None) if request.get_json() else None

        if agg_values:
            if agg_values.lower() not in ['true', 'false']:
                return error(status=400, detail="aggregate_values parameter not "
                             "must be either true or false")

            agg_values = eval(agg_values.title())

        if agg_values and agg_by:
            agg_list = ['day', 'week', 'quarter', 'month', 'year', 'julian_day', 'adm1', 'adm2']

            if agg_by.lower() not in agg_list:
                return error(status=400, detail="aggregate_by parameter not "
                             "in: {}".format(agg_list))

        if agg_by and not agg_values:
            return error(status=400, detail="aggregate_values parameter must be "
                                            "true in order to aggregate data")

        return func(*args, **kwargs)
    return wrapper


def validate_firetype(func):
    """Validate fire type"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        fire_type = request.args.get('fire_type')
        if fire_type:
            valid_fire_list = ['viirs', 'modis', 'all']
            if fire_type.lower() not in valid_fire_list:
                return error(status=400, detail='For this batch service, fire_type must one of {}'.format(', '.join(valid_fire_list)))

        return func(*args, **kwargs)
    return wrapper
