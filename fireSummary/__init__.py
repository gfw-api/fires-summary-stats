"""The API MODULE"""

import os
import logging

from flask import Flask
from fireSummary.config import SETTINGS
from fireSummary.routes.api import error
from fireSummary.routes.api.v1 import fires_endpoints, glad_endpoints
from fireSummary.utils.files import load_config_json
import RWAPIMicroservicePython

logging.basicConfig(
    level=SETTINGS.get('logging', {}).get('level'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y%m%d-%H:%M%p',
)

# Flask App
app = Flask(__name__)

# Routing
app.register_blueprint(fires_endpoints, url_prefix='/api/v1/fire-alerts')
app.register_blueprint(glad_endpoints, url_prefix='/api/v1/glad-alerts')
# CT
info = load_config_json('register')
swagger = load_config_json('swagger')
RWAPIMicroservicePython.register(
    app=app,
    name='fireSummary',
    info=info,
    swagger=swagger,
    mode=RWAPIMicroservicePython.AUTOREGISTER_MODE if os.getenv('CT_REGISTER_MODE') and os.getenv('CT_REGISTER_MODE') == 'auto' else RWAPIMicroservicePython.NORMAL_MODE,
    ct_url=os.getenv('CT_URL'),
    url=os.getenv('LOCAL_URL'),
    token=os.getenv('CT_TOKEN'),
    api_version=os.getenv('API_VERSION')
)


@app.errorhandler(403)
def forbidden(e):
    return error(status=403, detail='Forbidden')


@app.errorhandler(404)
def page_not_found(e):
    return error(status=404, detail='Not Found')


@app.errorhandler(405)
def method_not_allowed(e):
    return error(status=405, detail='Method Not Allowed')


@app.errorhandler(410)
def gone(e):
    return error(status=410, detail='Gone')


@app.errorhandler(500)
def internal_server_error(e):
    return error(status=500, detail='Internal Server Error')
