from __future__ import absolute_import
import aiohttp
import aiofiles
from config import SYSTEM_TOKEN_PATH
from logger import logger

TIMEOUT = aiohttp.ClientTimeout(total=5)

try:
    from config import SERVER_WG_BE_PHOENIX_METRICS
except Exception:
    SERVER_WG_BE_PHOENIX_METRICS = "http://wg-be-phoenix-metrics"


async def get_secret():
    async with aiofiles.open(SYSTEM_TOKEN_PATH, mode="rb") as f:
        contents = await f.read()
    secret = contents.decode().rstrip()
    logger.debug(f"readed from path: {secret}")
    return secret


async def push_metrics(_type, data):
    payload = {"data": data, "type": _type}
    logger.debug(f"pushing {data} to phoenix metrics")
    try:

        SYSTEM_TOKEN = await get_secret()
        headers_api_call = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        headers_api_call["Authorization"] = f"{SYSTEM_TOKEN}"
        path = "/v1/api/metrics"
        url = SERVER_WG_BE_PHOENIX_METRICS + path
        async with aiohttp.ClientSession(
            timeout=TIMEOUT, headers=headers_api_call
        ) as session:
            async with session.post(url, json=payload) as resp:
                resp.status
                resp = await resp.json()
                logger.debug(f"response from auz: {resp}")
    except Exception as e:
        logger.error(e)
        logger.error(e)
        logger.error(e)


async def push_metrics_auz_route_tracing_complete(data):
    await push_metrics("auz_route_tracing_complete", data)


async def push_metrics_auz_route_tracing_expired(data):
    await push_metrics("auz_route_tracing_expired", data)
