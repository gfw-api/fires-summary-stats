"""The API MODULE"""

import os
import logging

from flask import Flask
from fireSummary.config import SETTINGS
from fireSummary.routes.api import error
from fireSummary.routes.api.v1 import fires_endpoints, glad_endpoints
import RWAPIMicroservicePython

logging.basicConfig(
    level=SETTINGS.get("logging", {}).get("level"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y%m%d-%H:%M%p",
)
