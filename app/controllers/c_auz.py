from __future__ import absolute_import
from sanic.log import logger

# from sanic.response import json
import aiohttp
from config import TIMEOUT, SERVER_WG_BE_PHOENIX_AUT, SERVER_WG_BE_PHOENIX_MAIN
from exception import FormattedException

from models.m_user import User
from models.m_authorization_request import AuthorizationRequest
import re
import os
import binascii
import datetime
import time

"""
we need to check on different levels:

VIA gateway ui login:
this is a cookie so we set it as bearer token to pass in the gateway!
AUZ will retrieve it as a request.headers["authorization"] with bearer token

VIA API:
- system: is just the real system token put in request.headers["authorization"]
- api: is 'Bearer <access_token>' put in request.headers["authorization"]


"""

MEM = {}


def url_hash(url):
    return url.count("/")


async def generate_token(n=24, *args, **kwargs):
    return str(binascii.hexlify(os.urandom(n)), "utf-8")


async def check_token(auz_token):
    if auz_token in MEM:
        time_took = time.time() - MEM[auz_token]["time_stamp"]
        logger.debug(f"DELETING AUZ_TOKEN {MEM[auz_token]}, request took: {time_took}")
        del MEM[auz_token]
        return True
    else:
        raise "no token in memory"


async def allowed_route(payload, authorization_header):
    logger.debug("allowed_route called")
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
        logger.info("Authorization header found")

        if authorizationRequest.is_system_token:
            # SYSTEM TOKEN IS DIFFERENT ENDPOINT TO CHECK
            headers = {"authorization": authorizationRequest.authorization_header}
            try:
                async with aiohttp.ClientSession(
                    timeout=TIMEOUT, headers=headers
                ) as session:
                    async with session.get(
                        SERVER_WG_BE_PHOENIX_AUT + "/verify/system_token"
                    ) as resp:
                        status = resp.status
                        resp = await resp.json()
                if "role" in resp:  # stupid check to see if it is really a user
                    user = User(**resp)
                    logger.info(
                        f"System user: {user} trying to authorize with {authorizationRequest}"
                    )
                else:
                    raise FormattedException(
                        "Invalid system token", domain="auz", detail=resp, code=status
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
            headers = {"authorization": authorizationRequest.authorization_header}
            try:
                async with aiohttp.ClientSession(
                    timeout=TIMEOUT, headers=headers
                ) as session:
                    async with session.get(
                        SERVER_WG_BE_PHOENIX_AUT + "/auth/me"
                    ) as resp:
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
        "localhost:5050": "wg-be-phoenix-mailer",
    }

    if "localhost" in authorizationRequest.host or ":" in authorizationRequest.host:
        logger.debug("------------- TESTING ----------------")
        host = authorizationRequest.host.split("/")[0]  # with port
        host = hosts.get(host)
        authorizationRequest.host = host
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
                logger.debug(f"information retrieved from main first try: {resp}")
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN"
        )

    allowed_roles = None
    try:
        """
        here is some additional logic needed
        we can check a certain route on 3 different levels:
        1 on 1: /v1/api/users == /v1/api/users
        but what about /v1/api/id which is actually something like /v1/api/45jlfd-234fs-dfa-2....
        here we need a regex check. we can do a specific regex check or a general
        /v1/api/[A-z]+ is better then /v1/api/.+
        additional we need to have a certain hash check see url_hash
        """
        if status == 200:
            allowed_roles = resp["role"]
            logger.info(
                f"allowed roles for uri: {authorizationRequest.uri}: {allowed_roles}"
            )
        elif status == 400:  # which means nothing is found or something is wrong
            logger.debug(
                f"no allowed roles found at first for {authorizationRequest.uri} trying with regex matching"
            )
            hash_ = url_hash(authorizationRequest.uri)
            call = (
                SERVER_WG_BE_PHOENIX_MAIN
                + f"/v1/api/permission?host={authorizationRequest.host}&http_method={authorizationRequest.method}&url_hash={hash_}"
            )
            # 3 options nothing found again, 1 result or many
            # logger.info(f"Calling main on route: {call} by user: {user}")
            try:
                async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                    async with session.get(call) as resp:
                        status = resp.status
                        resp = await resp.json()
                        logger.debug(
                            f"information retrieved from main with url_hash: {resp}"
                        )
            except Exception as e:
                logger.error(e)
                raise FormattedException(
                    e, domain="auz", detail="There was a problem connecting to MAIN"
                )
            if status == 400:  # this means there are no urls
                raise "nothing found got from main: {resp}"
            elif status == 200:
                if "values" in resp:  # means there are multiple uri's returned
                    logger.debug("mutliple results returned to regex check")
                    # TODO add paging
                    for value in resp["values"]:
                        pattern = re.compile(f"^{value['uri']}$")
                        if re.match(f"^{value['uri']}$", authorizationRequest.uri):
                            logger.debug(
                                f"in multiple regex values got match {value['uri']}"
                            )
                            allowed_roles = value["role"]
                            break
                    else:
                        raise "no regex match found"

                elif (
                    "role" in resp
                ):  # this does not mean yet this is good, we need to check
                    logger.debug(f"single result returned to regex check")
                    pattern = re.compile(f"^{resp['uri']}$")
                    if pattern.match(authorizationRequest.uri):
                        logger.debug(f"in sigle regex check got match {resp['uri']}")
                        allowed_roles = resp["role"]
                    else:
                        raise "no regex match found"
                else:
                    raise "no routes found"
    except Exception as e:
        logger.error(
            f"uri {authorizationRequest.uri} doesn't exist or is not allowed to be accessed error: {e}"
        )
        raise FormattedException(
            "uri doesn't exist or is not allowed to be accessed", domain="auz", code=403
        )

    # ######################
    # CHECKING ROLES CAREFULL
    # ######################
    if not allowed_roles:
        logger.error("no allowed_roles")
        raise Exception("no allowed_roles")
    if "anonymous" in allowed_roles:
        pass
    elif user.role == "admin":
        pass
    elif user.role in allowed_roles:
        pass
    else:
        logger.info(
            f"User [{user}] does NOT have a correct role, userrole: [{user.role}] for [{authorizationRequest.method} {authorizationRequest.host} {authorizationRequest.uri}]"
        )
        raise FormattedException(
            "User does not have the correct access rights", domain="auz", code=403
        )
    logger.info(f"User {user} has correct role")

    # let us create a token and store it
    token = await generate_token()

    datetime_object = datetime.datetime.now()

    MEM[token] = {
        "uri": authorizationRequest.uri,
        "host": authorizationRequest.host,
        "method": authorizationRequest.method,
        "ip": authorizationRequest.ip,
        "created_at": str(datetime_object),
        "time_stamp": time.time(),
    }
    logger.debug(f"STORING AUZ_TOKEN {MEM[token]}")

    return {"allowed": True, "auz_token": token}
