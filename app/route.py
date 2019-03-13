from __future__ import absolute_import
from sanic import Blueprint
from routes import r_auz

"""
define routes groups here
"""

API = Blueprint("api", url_prefix="/api")
ROUTES = Blueprint.group(API, url_prefix="/")

API.add_route(
    r_auz.allowed_route, "/allowed", methods=["POST"], version="v1", strict_slashes=True
)
