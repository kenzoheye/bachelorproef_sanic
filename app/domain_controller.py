from __future__ import absolute_import
from controllers import c_auz
from sanic.log import logger
from exception import FormattedException


async def allowed_route(payload, authorization_header) -> dict:
    try:
        data = await c_auz.allowed_route(payload, authorization_header)
        return data
    except FormattedException as e:
        logger.error(e.formatted)
        raise e
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e,
            domain="allowed_route",
            detail="There was a problem checking if route is allowed",
        )


async def check_token(token, time_decorator=None) -> dict:
    try:
        data = await c_auz.check_token(token, time_decorator)
        return data
    except FormattedException as e:
        logger.error(e.formatted)
        raise e
    except Exception as e:
        logger.error(e)
        raise FormattedException(
            e,
            domain="check_token",
            detail="There was a problem checking if token is allowed",
        )
