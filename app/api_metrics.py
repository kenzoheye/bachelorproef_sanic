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


async def push_route_metrics(data):
    logger.debug(f"pushing {data} to phoenix metrics")
    try:

        headers_api_call = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        url = None
        # headers_api_call["Authorization"] = f"{SYSTEM_TOKEN}"
        payload = {"data": data, "type": "auz_route_tracing"}
        async with aiohttp.ClientSession(
            timeout=TIMEOUT, headers=headers_api_call
        ) as session:
            async with session.post(url, json=payload) as resp:
                resp.status
                resp = await resp.json()
    except Exception as e:
        raise e
