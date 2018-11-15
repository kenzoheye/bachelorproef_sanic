from sanic import Sanic
from sanic import Blueprint
from sanic.log import logger

from routes import ROUTES

app = Sanic(__name__)

# requests
app.config.REQUEST_MAX_SIZE = 100000000

app.blueprint(ROUTES)

logger.info("START WG-AUZSWITCH")

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        workers=1,
        debug=False,
        access_log=True,
        auto_reload=True,
    )
