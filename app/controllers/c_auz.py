from __future__ import absolute_import
from sanic.log import logger
from sanic.response import json
import aiohttp
from config import TIMEOUT, SERVER_WG_BE_PHOENIX_AUT, SERVER_WG_BE_PHOENIX_MAIN
from exception import FormattedException

from models.m_user import User
from models.m_authorization_request import AuthorizationRequest


async def allowed_route(payload, authorization_header):
    logger.debug(f"allowed_route called")
    try:
        authorizationRequest = AuthorizationRequest(
            **payload, authorization_header=authorization_header
        )
        logger.info(authorizationRequest)
    except KeyError as e:
        logger.error(f"There is a missing key in body: {e}")
        raise FormattedException(f"There is a missing key in body: {e}", domain="auz")
    except Exception as e:
        logger.error(e)
        raise FormattedException(f"Unable to create AuthorizationRequest", domain="auz")

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

    # SETTING THE DEFAULT USER OBJECT THIS IS NEEDED
    user = None
    if authorizationRequest.authorization_header:
        # logger.info("Authorization header found")
        headers = {"authorization": authorizationRequest.authorization_header}
        try:
            async with aiohttp.ClientSession(
                timeout=TIMEOUT, headers=headers
            ) as session:
                async with session.get(SERVER_WG_BE_PHOENIX_AUT + "/auth/me") as resp:
                    status = resp.status
                    resp = await resp.json()
            if resp.get("me"):
                user = User(**resp["me"])
                logger.info(
                    f"User {user} trying to authorize with {authorizationRequest}"
                )
            else:
                raise FormattedException(
                    "Invalid Bearer token", domain="auz", detail=resp, code=status
                )
        except FormattedException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise FormattedException(
                e,
                domain="auz",
                detail="There was a problem connecting to AUT",
                code=503,
            )
    else:
        user = User(role="anonymous")
        logger.info(f"User {user} trying to authorize with {authorizationRequest}")

    # ---- TESTING PURPOSES -----
    hosts = {
        "localhost:5000": "wg-be-api-car",
        "localhost:5001": "wg-be-phoenix-aut",
        "localhost:5002": "wg-be-phoenix-auz",
    }

    if "localhost" in authorizationRequest.host or ":" in authorizationRequest.host:
        logger.debug("------------- TESTING ----------------")
        host = authorizationRequest.host.split("/")[0]  # with port
        host = hosts.get(host)
    # ---- TESTING PURPOSES -----
    call = (
        SERVER_WG_BE_PHOENIX_MAIN
        + f"/v1/api/permission?host={authorizationRequest.host}&http_method={authorizationRequest.method}&uri={authorizationRequest.uri}"
    )
    logger.info(f"Calling main on route: {call} by user: {user}")
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(call) as resp:
                status = resp.status
                resp = await resp.json()
                logger.debug(f"information retrieved from main: {resp}")
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN"
        )
    try:
        allowed_roles = resp["role"]
    except Exception as e:
        logger.error(
            f"uri {authorizationRequest.uri} doesn't exist or is not allowed to be accessed error: {e}"
        )
        raise FormattedException(
            "uri doesn't exist or is not allowed to be accessed", domain="auz", code=403
        )
    # logger.info("user has role: " + role)

    # ROLE_WEIGHTS = {"admin": 1000, "system": 999, "superbroker": 100, "broker": 99,  "api": 5, "customer": 1, "anonymous": 0}
    logger.info(f"allowed roles on uri: {authorizationRequest.uri}: {allowed_roles}")

    # ######################
    # CHECKING ROLES CAREFULL
    # ######################
    if "anonymous" in allowed_roles:
        # if anonymous, everyone can pass
        return json({"allowed": True})
    elif user.role == "admin":
        # if admin, he can always pass
        return json({"allowed": True})
    elif user.role in allowed_roles:
        logger.info(f"User {user} has correct role")
        return json({"allowed": True})
    else:
        logger.info(f"User {user} does not have a correct role")
        raise FormattedException(
            "User does not have the correct access rights", domain="auz", code=403
        )
