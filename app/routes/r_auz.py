from __future__ import absolute_import
from __future__ import print_function
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
        payload = request.json
        logger.debug("REQUEST GOT IN ROUTE.PY: headers: {request.headers}")
        if "authorization" in request.headers:
            authorization_header = request.headers["authorization"]
            logger.info(
                f"REQUEST GOT: {payload}, HEADERS: {authorization_header[0:30]}"
            )
        else:
            authorization_header = None
            logger.info(f"REQUEST GOT: {payload}")
        return await dc.allowed_route(payload, authorization_header)
    except FormattedException as e:
        logger.error(e)
        logger.error(e.formatted)
        return json(e.formatted, status=e.formatted.get("code", 400))
    except Exception as e:
        logger.error(e)
        import traceback

        print((traceback.print_exc()))
        f = FormattedException(
            e, domain="auz", detail="There was a problem checking if route is allowed"
        )
        return json(f.formatted, status=f.formatted.get("code", 400))
