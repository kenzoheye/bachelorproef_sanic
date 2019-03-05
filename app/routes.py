from __future__ import absolute_import
from sanic import Blueprint


"""
define routes groups here
"""

API = Blueprint("api", url_prefix="/api")
ROUTES = Blueprint.group(API, url_prefix="/")
