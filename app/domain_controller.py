from controllers import c_auz
from sanic.log import logger


async def allowed_route(payload) -> dict:
    try:
        data = await c_auz.allowed_route(payload)
        logger.info(f"answer got: {data}")
        return data
    except Exception as e:
        logger.error(e)
        raise Exception(e)
