from __future__ import absolute_import
from sanic import Sanic
from sanic_openapi import openapi_blueprint, swagger_blueprint
from logger import LOGGING_CONFIG
from sanic.log import logger
from sanic_jwt import Initialize
from middleware.middleware import blueprint as middleware
from route import ROUTES
from config import SECRET
from controllers.c_auz import remove_old_entries_in_memory, remove_old_routes

app = Sanic(__name__, log_config=LOGGING_CONFIG, strict_slashes=True)

app.blueprint(middleware)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.blueprint(ROUTES)
# requests
app.config.REQUEST_MAX_SIZE = 100000000

Initialize(app, auth_mode=False, secret=SECRET)


@app.listener("after_server_start")
async def start_background_tasks_after_server_starts(app, loop):
    loop.create_task(remove_old_entries_in_memory())
    loop.create_task(remove_old_routes())


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
