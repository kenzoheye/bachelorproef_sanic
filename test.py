from __future__ import absolute_import
from __future__ import print_function
import requests

# host = "https://api.phoenix.dev.qa.wegroup.be"

host = "http://localhost:5002"
DEFAULT_TYPE = "application/vnd.api+json"
headers = {"content-type": DEFAULT_TYPE, "Accept": DEFAULT_TYPE}

post = "/v1/api/allowed"
# payload = {"email": "kenzo.heye@weaids2.be", "password": "123456789abcdef"}
# payload = {"email": "kenzo.heye@weaids2.be", "password": "123456789abcdef"}
r = requests.post(host + post, headers=headers)

print(r)
print((r.text))
exit(1)
print((r.json()))

tokens = r.json()

get = "/auth/me"
headers2 = headers
headers2["Authorization"] = "Bearer " + tokens.get("access_token")

print(headers2)
print("===================")
r = requests.get(host + get, headers=headers2)

print((r.text))
