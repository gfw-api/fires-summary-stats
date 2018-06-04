"""API ROUTER"""

import logging

from flask import jsonify, Blueprint
from ps.routes.api import error
from ps.validators import validate_greeting
from ps.middleware import set_something
from ps.serializers import serialize_greeting
import json
import CTRegisterMicroserviceFlask

psone_endpoints = Blueprint('psone_endpoints', __name__)


@psone_endpoints.route('/hello2', strict_slashes=False, methods=['GET'])
@set_something
@validate_greeting
def say_hello(something):
    """World Endpoint"""
    logging.info('[ROUTER]: Say Hello')
    config = {
        'uri': '/dataset',
        'method': 'GET',
    }
    response = CTRegisterMicroserviceFlask.request_to_microservice(config)
    elements = response.get('data', None) or 1
    data = {
        'word': 'hello',
        'propertyTwo': 'random',
        'propertyThree': elements,
        'something': something,
        'elements': 1
    }
    if False:
        return error(status=400, detail='Not valid')
    return jsonify(data=[serialize_greeting(data)]), 200


@psone_endpoints.route('/fires', strict_slashes=False, methods=['GET'])
@set_something
@validate_greeting
def say_hello3(something):
    """World Endpoint"""
    logging.info('[ROUTER]: Say Hello')
    config = {
        'uri': '/dataset',
        'method': 'GET',
    }
    response = CTRegisterMicroserviceFlask.request_to_microservice(config)
    elements = response.get('data', None) or 1
    data = {
        'word': 'this is fires',
        'propertyTwo': 'random',
        'propertyThree': elements,
        'something': something,
        'elements': 1
    }
    if False:
        return error(status=400, detail='Not valid')
    return jsonify(data=[serialize_greeting(data)]), 200

'''
https://production-api.globalforestwatch.org/query/4145f642-5455-4414-b214-58ad39b83e1e?sql=SELECT sum(fire_count) 
FROM data WHERE iso = 'IDN'

'''
