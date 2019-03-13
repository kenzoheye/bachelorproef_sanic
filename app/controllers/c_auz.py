from __future__ import absolute_import
from sanic.log import logger
from sanic.response import json
import aiohttp
from config import WG_BE_PHOENIX_AUT, TIMEOUT, WG_BE_PHOENIX_MAIN


async def allowed_route(request):
    logger.info("allowed")
    if request.json is None:
        return json({
            'domain': '/allowed',
            'detail': 'No body provided',
            'code': 400
        }, status=400)
    URI = request.json.get('URI', None)
    method = request.json.get('method', None)
    ip = request.json.get('ip', None)
    auth = request.headers.get('authorization', None)
    if URI is None:
        return json({
            'domain': '/allowed',
            'detail': 'No URI provided',
            'code': 400
        }, status=400)
    if method is None:
        return json({
            'domain': '/allowed',
            'detail': 'No method provided',
            'code': 400
        }, status=400)
    if ip is None:
        return json({
            'domain': '/allowed',
            'detail': 'No IP provided',
            'code': 400
        }, status=400)
    else:
        # IP TRACKING BEGIN -- TODO --
        """
        if ip_addresses.get(ip,None) is None:
            ip_addresses[ip] = {'blacklisted': False, 'calls':[]}

        caller = ip_addresses[ip]
        if caller.get('blacklisted'):
            return json({
                'domain': '/allowed',
                'detail': 'IP blacklisted',
                'code': 400
            }, status=400)
        call = {
            'time': time.time(),
            'uri': URI,
            'method': method,
            'auth': auth
        }
        caller.get('calls').append(call)
        """
        # IP TRACKING END -- TODO --
    role = 'anonymous'
    if auth is not None:
        logger.info("Authorization header found")
        headers = {"authorization": auth}
        async with aiohttp.ClientSession(timeout=TIMEOUT, headers=headers) as session:
            async with session.get(WG_BE_PHOENIX_AUT + '/auth/me') as resp:
                status = resp.status
                resp = await resp.json()
        if resp.get('me'):
            logger.info("User found!")
            logger.info(resp.get('me'))
            role = resp.get('me').get('role')
        else:
            return json(resp, status=status)

    logger.info(role)
    try:
        host = URI.replace("http://", "")
        uri = host[host.find('/'):len(host)]
        hosts = {
            'localhost:5000': 'wg-be-api-car',
            'localhost:5001': 'wg-be-phoenix-aut',
            'localhost:5002': 'wg-be-phoenix-auz'
        }

        if 'localhost' in host or ':' in host:
            host = host.split('/')[0]  # with port
            host = hosts.get(host)
        else:
            host = host.split(":")[0]  # without port

        get_permission = WG_BE_PHOENIX_MAIN + f'/v1/api/permission?host={host}&http_method={method}&uri={uri}'
        logger.info(get_permission)
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(get_permission) as resp:
                status = resp.status
                resp = await resp.json()
        logger.info('user role: ' + role)
        logger.info('allowed roles: ' + str(resp.get('role')))
        if role in resp.get('role'):
            logger.info("User has correct role")
            return json({
                'allowed': True
            })
        else:
            logger.info("User does not have the correct role")
            return json({
                'errors': [{
                        'domain': '/allowed',
                        'detail': 'User does not have the correct access rights',
                        'code': 403
                        }]
            }, status=403)
    except Exception as e:
        logger.info(e)
        return json({
            'errors': [{
                    'domain': '/allowed',
                    'detail': 'Permission does not exist or is not allowed to be accessed.',
                    'code': 400
                    }]
        }, status=400)
