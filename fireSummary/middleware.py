import sys

from functools import wraps
from utils import util


def valid_input_boundaries(func):
    """Set something"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['is_valid_combo'] = test_bad_combo(*args)
        return func(*args, **kwargs)
    return wrapper


def test_bad_combo(dataset_name, params):

    # get list of valid combos by reading in csv as json
    poly_iso_adm1_adm2_combos = util.load_valid_poly_iso(dataset_name)

    input_combo = [params['polyname'], params['iso_code'], params['adm1_code'], params['adm2_code']]
    input_combo = [x for x in input_combo if x is not None]
    input_len = len(input_combo)

    # get the same level of admin as the input:
    poly_iso_adm1_adm2_combos = [x[0:input_len] for x in poly_iso_adm1_adm2_combos]

    return input_combo in poly_iso_adm1_adm2_combos
