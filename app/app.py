from __future__ import absolute_import
from sanic import Sanic
from logger import LOGGING_CONFIG
from sanic.log import logger


app = Sanic(__name__, log_config=LOGGING_CONFIG)

# requests
app.config.REQUEST_MAX_SIZE = 100000000

# URLS = [
#     {"http_method": "POST", "uri": "/v1/api/users", "roles": ["user"]},
#     {"http_method": "GET", "uri": "/v1/api/users", "roles": []},
# ]
#
#
# async def check_auth(payload):
#     pass
#
#
# async def auz(get, uri, token=None):
#     verify = False
#     if token:
#         pass
#
#     for url in URLS:
#         if get == url["http_method" and uri == url[uri]]:
#             if not url["roles"]:
#                 verify = True
#
#     return verify
#
#
# @app.post("/", strict_slashes=True)
# @app.post("/auz", strict_slashes=True)
# async def post_auz(request):
#     try:
#
#         payload = request.json
#
#         # resp = await dc.authenticate(email=email, secret=secret)
#         resp = await auz(payload)
#
#         if "error" in resp:
#
#             raise Exception(json.dumps(resp["error"]))
#
#     except Exception as e:
#
#         logger.error(e)
#         return response.json({"errors": e.args}, status=400)
#
#     return response.json(resp, status=201)
#

logger.info("START WG-BE-PHOENIX-AUZ")

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5002,
        workers=1,
        debug=False,
        access_log=True,
        auto_reload=True,
    )
