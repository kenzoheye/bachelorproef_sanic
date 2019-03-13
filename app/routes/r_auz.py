from __future__ import absolute_import
from sanic_openapi import doc
from sanic.log import logger
from routes.models import AllowedConsumes
import domain_controller as dc


@doc.summary("Check if user has right credentials")
@doc.consumes(AllowedConsumes, location="body", content_type="application/vnd.api+json")
@doc.response(
    200,
    description="success",
    examples={
        "allowed": True,
        "allowed_roles": ["admin", "system", "superbroker"],
        "role": "admin",
        "allowed_methods": ["GET"],
        "method": "GET",
    },
)
@doc.response(
    400,
    description="error",
    examples={
        "domain": "/allowed",
        "detail": "URI does not exist or is not allowed to be accessed.",
        "code": 400,
    },
)
@doc.response(
    401,
    description="token invalid or expired",
    examples={"reasons": ["Signature has expired."], "exception": "Unauthorized"},
)
@doc.response(
    403,
    description="role not allowed",
    examples={
        "errors": [
            {
                "domain": "/allowed",
                "detail": "User does not have the access rights",
                "code": 403,
            }
        ]
    },
)
async def allowed_route(request):
    try:
        return await dc.allowed_route(request)
    except Exception as e:
        logger.error(e)
        return "error"
