from __future__ import absolute_import
from sanic_openapi import doc
from sanic.log import logger
from sanic.response import json
from routes.models import AllowedConsumes
import domain_controller as dc
from exception import FormattedException


@doc.summary("Check if user has right credentials")
@doc.consumes(AllowedConsumes, location="body", content_type="application/vnd.api+json")
@doc.response(200, description="success", examples={"allowed": True})
@doc.response(
    503,
    description="microservice down",
    examples={
        "domain": "auz",
        "msg": "111",
        "detail": "There was a problem connecting to AUT",
        "code": 503,
    },
)
@doc.response(
    401,
    description="token invalid or expired",
    examples={
        "domain": "auz",
        "msg": "Invalid Bearer token",
        "detail": {"reasons": ["Signature has expired."], "exception": "Unauthorized"},
        "code": 401,
    },
)
@doc.response(
    403,
    description="role not allowed",
    examples={
        "domain": "auz",
        "msg": "User does not have the correct access rights",
        "detail": None,
        "code": 403,
    },
)
@doc.response(
    400,
    description="error",
    examples={
        "domain": "auz",
        "msg": "There is a missing key in body: 'uri'",
        "detail": None,
        "code": 400,
    },
)
async def allowed_route(request):
    try:
        logger.info(f"REQUEST GOT: {request}")
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
