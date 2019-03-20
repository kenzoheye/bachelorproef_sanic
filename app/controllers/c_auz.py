from __future__ import absolute_import
from sanic.log import logger
from sanic.response import json
import aiohttp
from config import TIMEOUT, SERVER_WG_BE_PHOENIX_AUT, SERVER_WG_BE_PHOENIX_MAIN
from exception import FormattedException


async def allowed_route(request):
    try:
        uri = request.json["uri"]
        method = request.json["method"]
        request.json["ip"]
        host = request.json["host"]
        auth = request.headers.get("authorization")
    except KeyError as e:
        raise FormattedException(f"There is a missing key in body: {e}", domain="auz")

    # IP TRACKING BEGIN -- TODO --
    """
    if ip_addresses.get(ip,None) is None:
        ip_addresses[ip] = {'blacklisted': False, 'calls':[]}

    caller = ip_addresses[ip]
    if caller.get('blacklisted'):
        return json({
            'domain': 'auz',
            'detail': 'IP blacklisted',
            'code': 400
        }, status=400)
    call = {
        'time': time.time(),
        'uri': URI,
        'method': method,
        'auth': auth
    }
    caller.get('calls').append(call)
    """
    # IP TRACKING END -- TODO --
    role = "anonymous"
    if auth:
        logger.info("Authorization header found")
        headers = {"authorization": auth}
        try:
            async with aiohttp.ClientSession(
                timeout=TIMEOUT, headers=headers
            ) as session:
                async with session.get(SERVER_WG_BE_PHOENIX_AUT + "/auth/me") as resp:
                    status = resp.status
                    resp = await resp.json()
            if resp.get("me"):
                logger.info(f"User found: {resp.get('me')}")
                role = resp.get("me").get("role")
            else:
                raise FormattedException(
                    "Invalid Bearer token", domain="auz", detail=resp, code=status
                )
        except FormattedException as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise FormattedException(
                e,
                domain="auz",
                detail="There was a problem connecting to AUT",
                code=503,
            )

    logger.info("User role: " + role)
    # ---- TESTING PURPOSES -----
    hosts = {
        "localhost:5000": "wg-be-api-car",
        "localhost:5001": "wg-be-phoenix-aut",
        "localhost:5002": "wg-be-phoenix-auz",
    }
    logger.info(host)

    if "localhost" in host or ":" in host:
        host = host.split("/")[0]  # with port
        host = hosts.get(host)
    else:
        host = host.split(":")[0]  # without port
    # ---- TESTING PURPOSES -----
    call = (
        SERVER_WG_BE_PHOENIX_MAIN
        + f"/v1/api/permission?host={host}&http_method={method}&uri={uri}"
    )
    logger.info(f"Calling main on route: {call}")
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(call) as resp:
                status = resp.status
                resp = await resp.json()
    except Exception as e:
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN"
        )
    try:
        allowed_roles = resp["role"]
    except Exception:
        raise FormattedException(
            "URI doesn't exist or is not allowed to be accessed", domain="auz", code=403
        )
    logger.info("user has role: " + role)
    logger.info("allowed roles on uri: " + str(allowed_roles))
    if role in allowed_roles:
        logger.info("User has a correct role")
        return json({"allowed": True})
    else:
        logger.info("User does not have a correct role")
        raise FormattedException(
            "User does not have the correct access rights", domain="auz", code=403
        )
