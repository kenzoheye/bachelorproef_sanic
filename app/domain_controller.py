from __future__ import absolute_import
from controllers import c_auz
from sanic.log import logger
from exception import FormattedException


async def allowed_route(payload) -> dict:
    try:
        data = await c_auz.allowed_route(payload)
        logger.info(f"answer got: {data}")
        return data
    except FormattedException as e:
        logger.error("Formatted exception received")
        logger.error(e.formatted)
        raise e
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e,
            domain="allowed_route",
            detail="There was a problem checking if route is allowed",
        )
