from __future__ import absolute_import
import asyncio
import aiohttp
import time
import json
from logger import logger
from config import TIMEOUT as timeout
from six.moves import range

urls = [
    ("https://www.bitstamp.net/api/v2/ticker_hour/btceur/", "last"),
    ("https://api.coindesk.com/v1/bpi/currentprice.json", "bpi.EUR.rate_float"),
    ("https://blockchain.info/ticker", "EUR.last"),
    ("https://api.cryptonator.com/api/ticker/btc-eur", "ticker.price"),
    ("http://api.bitcoincharts.com/v1/weighted_prices.json", "EUR.24h"),
]


def check_prime(a):
    for i in range(2, a):
        if a % i == 0:
            return False
    return True


def find_prime(n):
    if check_prime(n):
        return n
    low = n - 1
    high = n + 1
    while True:
        if check_prime(low):
            return low
        elif check_prime(high):
            return high
        else:
            low -= 1
            high += 1
            time.sleep(0.01)


async def find_prime_async(n):
    if check_prime(n):
        return n
    low = n - 1
    high = n + 1
    while True:
        if check_prime(low):
            return low
        elif check_prime(high):
            return high
        else:
            low -= 1
            high += 1
            await asyncio.sleep(0.01)


async def getTestData():
    prices, timetook = await getBitcoinPricesAsync()
    t0 = time.time()

    tasks = []
    for p in prices:
        tasks.append(asyncio.create_task(find_prime_async(int(p))))

    prices = []
    for t in asyncio.as_completed(tasks):
        price = await t
        prices.append(price)

    sumprime = find_prime(sum(prices))
    t1 = time.time()
    timetook2 = round((t1 - t0) * 1000)

    return {
        "prices_nearest_prime": prices,
        "sum_nearest_price": sumprime,
        "timetook": timetook,
        "timetook_prime": timetook2,
    }


async def getTestDataSync():
    prices, timetook = await getBitcoinPricesSync()
    t0 = time.time()

    prices = list([find_prime(int(x)) for x in prices])

    sumprime = find_prime(sum(prices))

    t1 = time.time()
    timetook2 = round((t1 - t0) * 1000)

    return {
        "prices_nearest_prime": prices,
        "sum_nearest_price": sumprime,
        "timetook": timetook,
        "timetook_prime": timetook2,
    }


async def getBitcoinPricesSync():
    t0 = time.time()
    prices = []
    for url, root in urls:
        price = await getPrice(url, root)
        prices.append(float(price))
    t1 = time.time()
    timetook = round((t1 - t0) * 1000)
    return prices, timetook


async def getBitcoinPricesAsync():
    t0 = time.time()
    tasks = []
    for url, root in urls:
        tasks.append(asyncio.create_task(getPrice(url, root)))

    prices = []
    for t in asyncio.as_completed(tasks):
        price = await t
        prices.append(float(price))
    t1 = time.time()
    timetook = round((t1 - t0) * 1000)

    return prices, timetook


async def getPrice(url, root):
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            try:
                resp = await response.json()
            except Exception:
                resp = await response.text()
                resp = json.loads(resp)
    for subroot in root.split("."):
        try:
            resp = resp[subroot]
        except Exception as e:
            logger.error(e)
    return resp
