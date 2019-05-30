from __future__ import absolute_import
from __future__ import print_function
from logger import logger
from sanic.response import json
from controllers import c as controller


async def route_async(request):
    try:
        data = await controller.getTestData()
        return json(data, status=200)
    except Exception as e:
        logger.error(e)


async def route_sync(request):
    try:
        data = await controller.getTestDataSync()
        return json(data, status=200)
    except Exception as e:
        logger.error(e)
