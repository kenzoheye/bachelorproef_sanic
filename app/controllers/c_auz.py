from __future__ import absolute_import
from sanic.log import logger
from sanic.response import json
import aiohttp
from config import TIMEOUT, SERVER_WG_BE_PHOENIX_AUT, SERVER_WG_BE_PHOENIX_MAIN
from exception import FormattedException


class User(object):

    role = None
    system_token = None
    email = None
    description = ""

    def __init__(
        self, role, system_token=None, email=None, description=None, *args, **kwargs
    ):
        self.role = role
        if system_token:
            self.system_token = system_token
        if email:
            self.email = email
        if description:
            self.description = description

    def __repr__(self):
        if self.system_token:
            return f"<User [SYSTEM] {self.system_token} {self.role} {self.description}>"
        if self.email:
            return f"<User [USER] {self.email} {self.role} {self.description}>"


async def allowed_route(request):
    try:
        uri = request.json["uri"]
        method = request.json["method"]
        host = request.json["host"]
        auth = request.headers.get("Authorization")
        # this is here not to be used yet, but to make the user aware that an IP is needed to auth
        request.json["ip"]
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
    user = None
    if auth:
        logger.info(f"AUTHORIZATION HEADER found: {auth}")
        # logger.info("Authorization header found")
        headers = {"authorization": auth}
        try:
            async with aiohttp.ClientSession(
                timeout=TIMEOUT, headers=headers
            ) as session:
                async with session.get(SERVER_WG_BE_PHOENIX_AUT + "/auth/me") as resp:
                    status = resp.status
                    resp = await resp.json()
            if resp.get("me"):
                user = User(**resp["me"])
                # logger.info(f"User found: {resp.get('me')}")
                # role = resp.get("me").get("role")

                logger.info(f"User {user} authenticated")
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
    logger.info(f"Calling main on route: {call} by user: {user}")
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(call) as resp:
                status = resp.status
                resp = await resp.json()
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN"
        )
    try:
        allowed_roles = resp["role"]
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            "URI doesn't exist or is not allowed to be accessed", domain="auz", code=403
        )
    # logger.info("user has role: " + role)
    logger.info("allowed roles on uri: " + str(allowed_roles))
    if role in allowed_roles:
        logger.info(f"User {user} has a correct role")
        return json({"allowed": True})
    else:
        logger.info(f"User {user} does not have a correct role")
        raise FormattedException(
            "User does not have the correct access rights", domain="auz", code=403
        )
