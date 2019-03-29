from __future__ import absolute_import
from sanic import Blueprint
from sanic.log import logger
import aiohttp
from sanic.response import json
from config import TIMEOUT, SERVER_WG_BE_PHOENIX_AUZ

blueprint = Blueprint("middleware.middleware")

ALLOWED_ROUTES_WITHOUT_CREDS = ["/v1/api/allowed", "/swagger"]


@blueprint.middleware("request")
async def auth_middleware_test(request):
    """
    we need this function otherwise the auz is checking itself in a infinte loop
    """
    if request.path in ALLOWED_ROUTES_WITHOUT_CREDS:
        logger.debug(f"passing middleware, {request.path} accessed")
    else:
        logger.debug(f"not passing directly middleware, {request}")

        method = request.method
        host = request.host
        uri = request.path
        ip = None
        # TODO check if ip is public
        if "x-forwarded-for" in request.headers:
            ip = request.headers["x-forwarded-for"]
        if "x-real-ip" in request.headers:
            ip = request.headers["x-real-ip"]
        if ip is None:
            ip = request.ip

        body = {"uri": uri, "host": host, "method": method, "ip": ip}
        logger.info(f"calling auz with request {body}")
        auth = request.headers.get("authorization", None)
        timeout = TIMEOUT
        headers = {
            "content-type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        if auth is not None:
            headers["authorization"] = auth

        try:
            async with aiohttp.ClientSession(
                timeout=timeout, headers=headers
            ) as session:
                async with session.post(
                    SERVER_WG_BE_PHOENIX_AUZ + "/v1/api/allowed", json=body
                ) as resp:
                    logger.info(resp)
                    status = resp.status
                    resp = await resp.json()
                    logger.debug(f"response from AUZ: resp")
            allowed = resp.get("allowed", False)
            if not allowed:
                return json(resp, status=status)
        except Exception as e:
            logger.error(e)
            return json({"error": e})
