from __future__ import absolute_import
import aiohttp
import os

if os.environ.get("ENVIRONMENT") not in ["qa", "staging", "production"]:
    from dotenv import load_dotenv

    load_dotenv(verbose=True)

ENVIRONMENT = os.environ.get("ENVIRONMENT") or "qa"

TIMEOUT = aiohttp.ClientTimeout(total=180)
