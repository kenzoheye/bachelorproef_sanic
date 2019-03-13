import aiohttp
import os

if os.environ.get("ENVIRONMENT") not in ["qa", "staging", "production"]:
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

ENVIRONMENT = os.environ.get('ENVIRONMENT') or "qa"
SECRET = os.environ.get('secret') or 'star warz'

WG_BE_PHOENIX_AUT = os.environ.get('WG_BE_PHOENIX_AUT') or 'http://wg-be-phoenix-aut'
WG_BE_PHOENIX_AUZ = os.environ.get('WG_BE_PHOENIX_AUZ') or 'http://wg-be-phoenix-auz'
WG_BE_API_CAR = os.environ.get('WG_BE_API_CAR') or 'http://wg-be-api-car'
WG_BE_PHOENIX_MAIN = os.environ.get('WG_BE_PHOENIX_MAIN') or "http://wg-be-phoenix-main"

REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN') or None
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN') or None

API_TOKEN = os.environ.get('API_TOKEN') or 'XYZ'

TIMEOUT = aiohttp.ClientTimeout(total=180)
DEFAULT_TYPE = "application/vnd.api+json"
