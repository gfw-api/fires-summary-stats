from fireSummary.routes.api.v1.fires_router import fires_endpoints
from flask import jsonify

# GENERIC Error


def error(status=400, detail='Bad Request'):
    return jsonify(errors=[{
        'status': status,
        'detail': detail
    }]), status


