from __future__ import absolute_import
from sanic import Blueprint

blueprint = Blueprint("middleware.middleware")

# here are the allowed, routes, the not allowed routes are in api.permissions table
ALLOWED_ROUTES_WITHOUT_CREDS = ["/v1/api/allowed", "/swagger"]


@blueprint.middleware("request")
async def auz_token(request):
    pass
