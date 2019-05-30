from __future__ import absolute_import
from __future__ import print_function
import requests
import asyncio
import aiohttp
import time
from six.moves import range

timeout = TIMEOUT = aiohttp.ClientTimeout(total=180)
url_sync = "http://localhost:5002/api/sync"
url_async = "http://localhost:5002/api/async"


def call_route(url):
    r = requests.get(url)
    return r.json()


async def call_route_async(url, key):
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            resp = await response.json()
    return resp, key


def call_sync():
    t0 = time.time()
    sums = {"sync": {"timetook": 0, "prime": 0}, "async": {"timetook": 0, "prime": 0}}
    for _ in range(25):
        sync_sync = call_route(url_sync)
        sync_async = call_route(url_async)

        sums["sync"]["timetook"] += sync_sync["timetook"]
        sums["sync"]["prime"] += sync_sync["timetook_prime"]

        sums["async"]["timetook"] += sync_async["timetook"]
        sums["async"]["prime"] += sync_async["timetook_prime"]
    t1 = time.time()
    print(f"[SYNCHRONOUS] Time took: {round(t1-t0, 2)} seconds")
    print(("SUMS", sums))


async def call_async():
    t0 = time.time()
    sums = {"sync": {"timetook": 0, "prime": 0}, "async": {"timetook": 0, "prime": 0}}

    tasks = []
    for _ in range(25):
        tasks.append(asyncio.create_task(call_route_async(url_sync, "sync")))
        tasks.append(asyncio.create_task(call_route_async(url_async, "async")))

    for t in asyncio.as_completed(tasks):
        result, key = await t
        sums[key]["timetook"] += result["timetook"]
        sums[key]["prime"] += result["timetook_prime"]

    t1 = time.time()
    print(f"[ASYNCHRONOUS] Time took: {round(t1-t0, 2)} seconds")
    print(("SUMS", sums))


async def main():
    call_sync()
    await call_async()


asyncio.run(main())
