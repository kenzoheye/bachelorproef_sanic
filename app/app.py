from __future__ import absolute_import
from sanic import Sanic
from logger import LOGGING_CONFIG
from logger import logger
from middleware.middleware import blueprint as middleware
from route import ROUTES

app = Sanic(__name__, log_config=LOGGING_CONFIG, strict_slashes=True)

app.blueprint(middleware)
app.blueprint(ROUTES)
# requests
app.config.REQUEST_MAX_SIZE = 100000000


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
