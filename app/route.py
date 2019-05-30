from __future__ import absolute_import
from sanic import Blueprint
from routes import r as routes

"""
define routes groups here
"""

API = Blueprint("api", url_prefix="/api")
ROUTES = Blueprint.group(API, url_prefix="/")

API.add_route(routes.route_async, "/async", methods=["GET"])

API.add_route(routes.route_sync, "/sync", methods=["GET"])

# API.add_route(
#     r_auz.allowed_route, "/allowed", methods=["POST"], version="v1", strict_slashes=True
# )
# API.add_route(
#     r_auz.check_token,
#     "/check_token",
#     methods=["POST"],
#     version="v1",
#     strict_slashes=True,
# )
# API.add_route(
#     r_auz.get_role_from_auz_token,
#     "/auz_token/info/role",
#     methods=["GET"],
#     version="v1",
#     strict_slashes=True,
# )
