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
from copy import deepcopy
import asyncio
from api_metrics import (
    push_metrics_auz_route_tracing_complete,
    push_metrics_auz_route_tracing_expired,
)

CACHE_EXPIRATION_DELTA = 3 * 60 * 60

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
ROUTES_MEM = {}


async def remove_old_entries_in_memory():
    while True:
        try:
            # every 5 minutes 300
            await asyncio.sleep(300)
            logger.debug("Removing old sessions routine started")
            now_plus_10min = time.time() + 600

            _memory = deepcopy(MEM)

            for k, v in _memory.items():
                if v["time_stamp"] > now_plus_10min:
                    logger.info(f"removing old entry, older then 6 hours: {MEM[k]}")
                    loop = asyncio.get_event_loop()
                    loop.create_task(push_metrics_auz_route_tracing_expired(MEM[k]))
                    del MEM[k]

            del _memory
            del now_plus_10min
        except Exception as e:
            logger.error("Cannot remove old session")
            logger.error(e)


async def remove_old_routes():
    """
    Removes all the entries in ROUTES_MEM that have expired (older than 3 hours)
    This function checks the dict every 5 minutes (see app.py)
    """
    while True:
        try:
            await asyncio.sleep(300)
            logger.debug("Removing routes routine started")

            _memory = deepcopy(ROUTES_MEM)
            for k, v in _memory.items():
                if v.get("exp") and v["exp"] > time.time():
                    logger.info(
                        f"[REMOVING_ROUTES] Removing old entry, older than 3 hours: {ROUTES_MEM[k]}"
                    )
                    del ROUTES_MEM[k]
                else:
                    for regex_k, regex_v in v.items():
                        if regex_v.get("exp") and regex_v["exp"] > time.time():
                            logger.info(
                                f"[REMOVING_ROUTES] Removing old entry, older than 3 hours: {ROUTES_MEM[k][regex_k]}"
                            )
                            del ROUTES_MEM[k][regex_k]
                        if len(ROUTES_MEM[k]) == 0:
                            del ROUTES_MEM[k]

            del _memory
        except Exception as e:
            logger.error(e)
            logger.error("Cannot remove routes")


def url_hash(url):
    """
    counts the amount of slashes in an uri
    """
    return url.count("/")


async def generate_store_token(authorizationRequest, user, n=24):
    token = str(binascii.hexlify(os.urandom(n)), "utf-8")
    datetime_object = datetime.datetime.now()

    # TODO add user to dict via dataclasses
    MEM[token] = {
        "uri": authorizationRequest.uri,
        "host": authorizationRequest.host,
        "method": authorizationRequest.method,
        "ip": authorizationRequest.ip,
        "created_at": str(datetime_object),
        "time_stamp": time.time(),
        "user_role": user.role,
        "user_email": user.email,
        "user_system_token": user.system_token,
    }
    logger.debug(f"STORING AUZ_TOKEN {MEM[token]}")
    return token


async def check_token(auz_token, time_decorator=None):
    now = time.time()
    if auz_token in MEM:
        time_took = now - MEM[auz_token]["time_stamp"]
        metrics_object = MEM[auz_token].copy()
        metrics_object["time_took"] = time_took
        logger.debug(f"DELETING AUZ_TOKEN {MEM[auz_token]}, request took: {time_took}")
        loop = asyncio.get_event_loop()
        MEM[auz_token]["time_took"] = time_took

        if time_decorator:
            MEM[auz_token]["time_took_plus_decorator"] = now - time_decorator
        loop.create_task(push_metrics_auz_route_tracing_complete(MEM[auz_token]))
        del metrics_object
        del MEM[auz_token]
        return True
    else:
        raise "no token in memory"


async def get_role_by_auz_token(auz_token):

    if auz_token in MEM:
        role = MEM[auz_token]["user_role"]
    else:
        raise Exception("no such auz_token")
    return {"role": role}


async def get_roles_from_regex_route(authorizationRequest: AuthorizationRequest):
    """
    First, checks the cached routes for roles and then gets the roles from the route in the database
    checks if the route matches the regex check in the database and if it does returns the roles and caller
    """
    hash_ = url_hash(authorizationRequest.uri)
    call = (
        SERVER_WG_BE_PHOENIX_MAIN
        + f"/v1/api/permission?host={authorizationRequest.host}&http_method={authorizationRequest.method}&url_hash={hash_}"
    )
    logger.info(f"Checking role for REGEX route: {call}")
    if call in ROUTES_MEM:
        for regex, value in ROUTES_MEM[call].items():
            if re.match(regex, authorizationRequest.uri):
                return value.get("roles"), value.get("callers")

    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(call) as resp:
                resp = await resp.json()
                logger.debug(f"ANSWER GOT FROM MAIN: {resp}")

    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN", code=503
        )
    roles = None
    callers = None

    if "role" in resp:
        regex = f'^{resp["uri"]}$'
        if re.match(regex, authorizationRequest.uri):
            roles = resp.get("role")
            callers = resp.get("caller")
            if not ROUTES_MEM.get(call):
                ROUTES_MEM[call] = {}
            ROUTES_MEM[call][resp["uri"]] = {
                "roles": roles,
                "callers": callers,
                "exp": int(time.time() + CACHE_EXPIRATION_DELTA),
            }

    elif "values" in resp:
        for val in resp["values"]:
            regex = f'^{val["uri"]}$'
            if re.match(regex, authorizationRequest.uri):
                roles = val.get("role")
                callers = val.get("caller")
                if not ROUTES_MEM.get(call):
                    ROUTES_MEM[call] = {}
                ROUTES_MEM[call][val["uri"]] = {
                    "roles": roles,
                    "callers": callers,
                    "exp": int(time.time() + CACHE_EXPIRATION_DELTA),
                }
                break
    return roles, callers


async def get_roles_from_route(authorizationRequest: AuthorizationRequest):
    """
    First, checks the cached routes for roles and then gets the roles from the route in the database
    returns the role and caller for the found route
    """

    call = (
        SERVER_WG_BE_PHOENIX_MAIN
        + f"/v1/api/permission?host={authorizationRequest.host}&http_method={authorizationRequest.method}&uri={authorizationRequest.uri}"
    )
    if call in list(ROUTES_MEM.keys()):
        return ROUTES_MEM[call].get("roles"), ROUTES_MEM[call].get("callers")
    logger.info(f"Checking role for route: {call}")
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(call) as resp:
                resp = await resp.json()
                logger.debug(f"ANSWER GOT FROM MAIN: {resp}")

    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to MAIN", code=503
        )
    roles = resp.get("role")
    callers = resp.get("caller")
    if roles:
        ROUTES_MEM[call] = {
            "roles": roles,
            "callers": callers,
            "exp": int(time.time() + CACHE_EXPIRATION_DELTA),
        }

    return roles, callers


async def get_user(authorizationRequest: AuthorizationRequest):
    """
    Retrieves a user object from WG-BE-PHOENIX-AUT with given Bearer token
    """
    headers = {"authorization": authorizationRequest.authorization_header}
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT, headers=headers) as session:
            resp = await session.get(SERVER_WG_BE_PHOENIX_AUT + "/auth/me")
            resp = await resp.json()

            return resp

    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to AUT", code=503
        )


async def get_system(authorizationRequest: AuthorizationRequest):
    """
    Retrieves a system user object from WG-BE-PHOENIX-AUT with given System token
    """
    headers = {"authorization": authorizationRequest.authorization_header}
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT, headers=headers) as session:
            resp = await session.get(SERVER_WG_BE_PHOENIX_AUT + "/verify/system_token")
            resp = await resp.json()
            return resp

    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e, domain="auz", detail="There was a problem connecting to AUT", code=503
        )


async def allowed_route(payload, authorization_header=None):
    """
    Checks if the user can call a specific route on a specific microservice with their role

    Args:
        payload:
            host: name of the microservice
            method: http method
            uri: endpoint to call on microservice
            ip: ip of caller
    """
    logger.debug("[ENTERED AUZ] allowed_route called")
    try:
        authorizationRequest = AuthorizationRequest(
            **payload, authorization_header=authorization_header
        )
    except TypeError as e:
        logger.error(f"Missing arguments: {e}")
        raise FormattedException(f"There is a missing key in body: {e}", domain="auz")
    except Exception as e:
        logger.error(type(e))
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
    # TODO -- IP TRACKING END

    # SETTING THE DEFAULT USER OBJECT THIS IS NEEDED
    user = User(role="anonymous")
    invalid_token_error = None
    if authorizationRequest.authorization_header:
        if authorizationRequest.is_system_token:
            logger.info("Authorization header is a SYSTEM_TOKEN!")
            userdata = await get_system(authorizationRequest)
        else:
            logger.info("Authorization header is a USER!")
            userdata = await get_user(authorizationRequest)
        try:
            if "exception" in userdata:
                reasons = {
                    "Signature has expired.": "TOKEN_EXPIRED",
                    "Auth required.": "TOKEN_INVALID",
                }
                msg = reasons.get(userdata["reasons"][0])
                if msg is None:
                    msg = "TOKEN_INVALID"
                invalid_token_error = FormattedException(
                    msg, detail=userdata["reasons"][0], domain="auz", code=401
                )
            else:
                if userdata.get("me"):
                    user = User(**userdata["me"])
                else:
                    user = User(**userdata)
                if user.role == "admin":
                    logger.info("===== USER ROLE IS ADMIN SKIPPING ROUTE CHECK =====")
                    token = await generate_store_token(authorizationRequest, user)
                    return {"allowed": True, "auz_token": token}
        except Exception as e:
            logger.error(e)
            raise FormattedException(
                e, domain="auz", detail="Did not get valid userdata", code=400
            )

    # ---- TESTING PURPOSES -----
    hosts = {
        "localhost:5000": "wg-be-api-car",
        "localhost:5001": "wg-be-phoenix-aut",
        "localhost:5002": "wg-be-phoenix-auz",
        "localhost:5020": "wg-be-api-quotes",
        "localhost:5050": "wg-be-phoenix-mailer",
    }

    if "localhost" in authorizationRequest.host or ":" in authorizationRequest.host:
        logger.debug("------------- TESTING ----------------")
        logger.debug(f"LOCALHOST TESTING WITH : {authorizationRequest}")
        host = authorizationRequest.host.split("/")[0]  # with port
        host = hosts.get(host)
        authorizationRequest.host = host
    # ---- TESTING PURPOSES -----

    role_tasks = [
        asyncio.create_task(get_roles_from_route(authorizationRequest)),
        asyncio.create_task(get_roles_from_regex_route(authorizationRequest)),
    ]

    logger.debug("==========STARTING ROUTE TASKS NOW==========")
    allowed_roles = None
    for t in asyncio.as_completed(role_tasks):
        role, caller = await t
        if role:
            logger.debug(f"ROLE FOUND IN ROUTE: {role}")
            if "anonymous" in role:
                token = await generate_store_token(authorizationRequest, user)
                return {"allowed": True, "auz_token": token}
            allowed_roles = role
            allowed_callers = caller
            break
    logger.debug("==========ROUTE TASKS FINISHED==========")
    if not allowed_roles:
        raise FormattedException(
            "URI_DOESNT_EXIST",
            domain="auz",
            detail="URI does not exist or method is not allowed",
            code=404,
        )

    # ? ######################
    # ! CHECKING ROLES
    # ? ######################

    elif user.role in allowed_roles and (
        not allowed_callers or user.caller in allowed_callers
    ):
        pass
    elif invalid_token_error is not None:
        raise invalid_token_error
    else:
        logger.info(
            f"User [{user}] does NOT have a correct role, userrole: [{user.role}] caller: [{user.caller}] for [{authorizationRequest.method} {authorizationRequest.host} {authorizationRequest.uri}]"
        )
        raise FormattedException(
            "USER_NOT_ALLOWED",
            detail="User does not have the correct access rights",
            domain="auz",
            code=403,
        )

    # let us create a token and store it, for the route
    token = await generate_store_token(authorizationRequest, user)

    return {"allowed": True, "auz_token": token}
