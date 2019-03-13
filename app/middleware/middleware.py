from sanic import Blueprint
from sanic.log import logger
import aiohttp
from sanic.response import json
from config import WG_BE_PHOENIX_AUZ, TIMEOUT

# json

# from errors import format_error
# from logger import logger

# from sanic.log import logger

blueprint = Blueprint("middleware.middleware")


@blueprint.middleware("request")
async def auth_middleware_test(request):
    logger.warning(request.path)
    if '/v1/api/allowed' == request.path or '/swagger' in request.path or '/openapi' in request.path:
        logger.info('/allowed accessed')
    else:
        logger.info('middleware')
        method = request.method
        uri = request.url
        ip = None
        # TODO check if ip is public
        if "x-forwarded-for" in request.headers:
            ip = request.headers["x-forwarded-for"]
        if "x-real-ip" in request.headers:
            ip = request.headers["x-real-ip"]
        if ip is None:
            ip = request.ip

        body = {
            'URI': uri,
            'method': method.upper(),
            "ip": ip
        }
        auth = request.headers.get('authorization', None)
        timeout = TIMEOUT
        headers = {"content-type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}
        if auth is not None:
            headers['authorization'] = auth
        logger.info(headers)
        try:
            AUZ = WG_BE_PHOENIX_AUZ
            if request.host == '127.0.0.1:42101':
                AUZ = 'http://127.0.0.1:42101'
            logger.info('CONNECTING TO AUZ ON: ' + AUZ)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.post(AUZ + '/v1/api/allowed', json=body) as resp:
                    logger.info(resp)
                    status = resp.status
                    resp = await resp.json()
            logger.info(resp)
            allowed = resp.get('allowed', False)
            if not allowed:
                return json(resp, status=status)
        except Exception as e:
            return json({'error': e})
