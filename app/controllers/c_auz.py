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
    description = "no description"

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
            return f"<User [SYSTEM] {self.system_token[0:30]} {self.role} {self.description}>"
        if self.email:
            return f"<User [USER] {self.email} {self.role} {self.description}>"


class AuthorizationRequest(object):

    host = None
    method = None
    uri = None
    ip = None
    authorization_header = None

    def __init__(
        self, host, method, uri, ip, authorization_header=None, *args, **kwargs
    ):
        if args:
            logger.debug(f"got to many arguments for args: {args}")
        if kwargs:
            logger.debug(f"got to many arguments for kwargs: {kwargs}")

        self.host = host
        self.method = method
        self.uri = uri
        self.ip = ip
        self.authorization_header = authorization_header

    def __repr__(self):
        if self.authorization_header:
            return f"<AuthorizationRequest {self.host} {self.method} {self.uri} {self.authorization_header[0:30]} from {self.ip}>"
        else:
            return f"<AuthorizationRequest {self.host} {self.method} {self.uri} from {self.ip}>"


async def allowed_route(payload, authorization_header):
    try:
        authorizationRequest = AuthorizationRequest(
            **payload, authorization_header=authorization_header
        )
        logger.info(authorizationRequest)
        # this is here not to be used yet, but to make the user aware that an IP is needed to auth
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
                logger.info(f"User {user} got from auz")
                logger.info(
                    f"User {user} trying to authorize with {authorizationRequest}"
                )
                # setting the role to the user role
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
        logger.info(f"User anonymous trying to authorize with {authorizationRequest}")

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
    else:
        host = authorizationRequest.host.split(":")[0]  # without port
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
    logger.info(f"allowed roles on uri: {authorizationRequest.uri}: {allowed_roles}")
    role = user.role if hasattr(user, "role") else "anonymous"
    if role in allowed_roles:
        logger.info(f"User {user} has correct role")
        return json({"allowed": True})
    else:
        logger.info(f"User {user} does not have a correct role")
        raise FormattedException(
            "User does not have the correct access rights", domain="auz", code=403
        )
