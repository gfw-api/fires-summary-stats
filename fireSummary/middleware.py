import json
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


def test_valid_admin(poly_iso_adm1_adm2_combos, input_admin_combo):
    # create list of iso/adm1 & iso/adm1/adm2 combos
    valid_iso_adm1 = [x[1:3] for x in poly_iso_adm1_adm2_combos]
    valid_iso_adm1_adm2 = [x[1:4] for x in poly_iso_adm1_adm2_combos]

    # admin combo lookup
    admin_combo_dict = {2: valid_iso_adm1, 3: valid_iso_adm1_adm2}

    admin_input_length = len(input_admin_combo)

    # valid admin reponse
    valid_admin_combo = admin_combo_dict[admin_input_length]

    if not input_admin_combo in valid_admin_combo:
        sys.exit()


def test_bad_combo(polyname, iso_code, adm1_code=None, adm2_code=None):
    # get list of valid combos by reading in csv as json
    poly_iso_adm1_adm2_combos = util.load_valid_poly_iso()

    input_combo = [polyname, iso_code, adm1_code, adm2_code]
    input_combo = [x for x in input_combo if x is not None]
    input_len = len(input_combo)

    # get the same level of admin as the input:
    poly_iso_adm1_adm2_combos = [x[0:input_len] for x in poly_iso_adm1_adm2_combos]

    return input_combo in poly_iso_adm1_adm2_combos



