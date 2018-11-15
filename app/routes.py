from sanic import Blueprint
from sanic import response

import domain_controller as dc

"""
define routes groups here
"""

ROUTES = Blueprint("routes", url_prefix="/")


async def get_auz(request):

    auz = await dc.get_auz()

    return response.json(auz)


"""
Declare all routes here for overview
"""

ROUTES.add_route(get_auz, "/", methods=["GET"])
