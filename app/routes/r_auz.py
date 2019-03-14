from __future__ import absolute_import
from sanic_openapi import doc
from sanic.log import logger
from sanic.response import json
from routes.models import AllowedConsumes
import domain_controller as dc
from exception import FormattedException


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
        "detail": "There was a problem checking if route is allowed",
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
    except FormattedException as e:
        logger.error(e)
        logger.error(e.formatted)
        return json(e.formatted, status=e.formatted.get("code", 400))
    except Exception as e:
        logger.error(e)
        f = FormattedException(
            e, domain="auz", detail="There was a problem checking if route is allowed"
        )
        return json(f.formatted, status=f.formatted.get("code", 400))
