from __future__ import absolute_import
import aiohttp
import os

if os.environ.get("ENVIRONMENT") not in ["qa", "staging", "production"]:
    from dotenv import load_dotenv

    load_dotenv(verbose=True)

ENVIRONMENT = os.environ.get("ENVIRONMENT") or "qa"
SECRET = (
    os.environ.get("JWT_SIGNATURE_SECRET")
    or "58HHzpBu7iRAvYK5C01YgktNP7LbiPuBWrjgn4AjtFiunDjTX7fuVx6aCaERSyXC"
)

SERVER_WG_BE_PHOENIX_AUT = (
    os.environ.get("SERVER_WG_BE_PHOENIX_AUT") or "http://wg-be-phoenix-aut"
)
SERVER_WG_BE_PHOENIX_AUZ = (
    os.environ.get("SERVER_WG_BE_PHOENIX_AUZ") or "http://wg-be-phoenix-auz"
)
SERVER_WG_BE_PHOENIX_MAIN = (
    os.environ.get("SERVER_WG_BE_PHOENIX_MAIN") or "http://wg-be-phoenix-main"
)

# REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN") or None
# ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN") or None
# SYSTEM_TOKEN = os.environ.get("SYSTEM_TOKEN") or None

TIMEOUT = aiohttp.ClientTimeout(total=180)

SYSTEM_TOKEN_PATH = os.environ.get("SYSTEM_TOKEN_PATH") or "/var/run"
