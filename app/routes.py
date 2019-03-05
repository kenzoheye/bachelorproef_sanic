from sanic import Blueprint
from sanic import response
from sanic_openapi import doc
from sanic.log import logger
import json
from logger import log

import domain_controller as dc

"""
define routes groups here
"""

API = Blueprint("api", url_prefix="/api")
ROUTES = Blueprint.group(API, url_prefix="/")

"""
Declare all routes here for overview
"""


@API.post("/auz", version="v1", strict_slashes=True)
    try:

        args = request.json

        if "email" not in args:

            raise Exception("no email provided! use {'email': 'email'}")

        if "secret" not in args:

            raise Exception("no secret provided! use {'secret': 'secret'}")

        email = args["email"]
        secret = args["secret"]

        resp = await dc.authenticate(email=email, secret=secret)

        if "error" in resp:

            raise Exception(json.dumps(resp["error"]))

    except Exception as e:

        logger.error(e)
        return response.json({"errors": e.args}, status=400)

    return response.json(resp, status=201)

@doc.summary("authenticates a user")
@doc.consumes(
    {"body": {"email": str, "secret": str}},
    location="body",
    content_type="application/json",
)
@doc.response(201, description="successful operation", examples={"user": "TODO"})
@doc.response(400, description="error", examples={"errors": ["error"]})
@doc.response(599, description="rate limit")
async def auth(request):

    # auth user
    # store user
    # retrieve token
    try:

        args = request.json

        if "email" not in args:

            raise Exception("no email provided! use {'email': 'email'}")

        if "secret" not in args:

            raise Exception("no secret provided! use {'secret': 'secret'}")

        email = args["email"]
        secret = args["secret"]

        resp = await dc.authenticate(email=email, secret=secret)

        if "error" in resp:

            raise Exception(json.dumps(resp["error"]))

    except Exception as e:

        logger.error(e)
        return response.json({"errors": e.args}, status=400)

    return response.json(resp, status=201)


@API.post("/auth/me", version="v1", strict_slashes=True)
async def auth_me(request):

    # get the token and check user and send user information
    pass


@API.post("/auth/refresh", version="v1", strict_slashes=True)
async def auth_refresh(request):

    # refresh token
    pass


@API.post("/auth/verify", version="v1", strict_slashes=True)
async def auth_verify(request):

    # verify token
    pass
