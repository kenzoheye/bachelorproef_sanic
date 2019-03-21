from __future__ import absolute_import
from __future__ import print_function
from app import app
from config import WG_BE_PHOENIX_AUT
import requests
import unittest

print("testing")
DEFAULT_TYPE = "application/vnd.api+json"


class AutoTest(unittest.TestCase):
    def test_index_anon_no_token(self):
        print("TEST_INDEX_ANON_NO_TOKEN")
        request, response = app.test_client.get("/")

        error = response.json.get("errors")[0]
        self.assertEqual(error.get("domain", None), "/v1/api/allowed")
        self.assertEqual(response.status, 400)

    def test_index_invalid_token(self):
        print("TEST_INDEX_INVALID_TOKEN")
        a_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia2Vuem8uaGV5ZUB3ZWdyb3VwLmJlIiwiZXhwIjoxNTUxOTUzNjc4fQ.1p-NvMiT6N1OBu-fBA1l_HDPvQWwTyl9YkwIIFSlO2A"
        headers = {"authorization": "Bearer " + a_token}
        request, response = app.test_client.get("/", headers=headers)

        self.assertEqual(response.json.get("exception", None), "Unauthorized")
        self.assertIsNotNone(response.json.get("reasons", None))

    def test_index_valid_token(self):
        print("TEST_INDEX_VALID_TOKEN")
        body = {"email": "kenzo.heye@weaids2.be", "password": "123456789abcdef"}
        headers = {"Content-Type": DEFAULT_TYPE, "Accept": DEFAULT_TYPE}
        # async with aiohttp.ClientSession(timeout=TIMEOUT, headers=headers) as session:
        #    async with session.post(AUT+ '/auth', json=body) as resp:
        #        resp = await resp.json()
        resp = requests.post(WG_BE_PHOENIX_AUT + "/auth", json=body, headers=headers)
        resp = resp.json()
        self.assertIsNotNone(resp.get("access_token", None))
        headers["Authorization"] = "Bearer " + resp.get("access_token")

        request, response = app.test_client.get("/", headers=headers)

    def test_allowed_no_body(self):
        request, response = app.test_client.post("/v1/api/allowed")
        resp = response.json
        self.assertEqual(response.status, 400)
        self.assertEqual(resp.get("detail"), "No body provided")

    def test_allowed_empty_body(self):
        body = {}
        request, response = app.test_client.post("/v1/api/allowed", json=body)
        resp = response.json
        self.assertEqual(response.status, 400)
        self.assertEqual(resp.get("detail"), "No URI provided")

    def test_allowed_no_method(self):
        body = {"URI": "localhost:5001/"}
        request, response = app.test_client.post("/v1/api/allowed", json=body)
        resp = response.json
        self.assertEqual(response.status, 400)
        self.assertEqual(resp.get("detail"), "No method provided")

    def test_allowed_no_IP(self):
        body = {"URI": "localhost:5001/", "method": "GET"}
        request, response = app.test_client.post("/v1/api/allowed", json=body)
        resp = response.json
        self.assertEqual(response.status, 400)
        self.assertEqual(resp.get("detail"), "No IP provided")

    def test_allowed_anon_true(self):
        body = {
            "URI": "http://localhost:5001/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        request, response = app.test_client.post("/v1/api/allowed", json=body)
        resp = response.json
        clog(resp)
        self.assertEqual(response.status, 200)
        self.assertTrue(resp.get("allowed"))

    def test_allowed_anon_false(self):
        body = {
            "URI": "http://localhost:5002/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        request, response = app.test_client.post("/v1/api/allowed", json=body)
        resp = response.json
        clog(resp)
        self.assertEqual(response.status, 403)

    def test_allowed_auth_expired_token(self):
        body = {
            "URI": "http://localhost:5002/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        headers = {
            "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia2Vuem8uaGV5ZUB3ZWdyb3VwLmJlIiwiZXhwIjoxNTUxOTUzNjc4fQ.1p-NvMiT6N1OBu-fBA1l_HDPvQWwTyl9YkwIIFSlO2A"
        }
        request, response = app.test_client.post(
            "/v1/api/allowed", json=body, headers=headers
        )
        resp = response.json
        self.assertEqual(response.status, 401)
        self.assertEqual(resp.get("reasons")[0], "Signature has expired.")

    def test_allowed_auth_invalid_token(self):
        body = {
            "URI": "http://localhost:5002/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        headers = {
            "authorization": "Bearer eyJ0eXAiOiJK1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoia2Vuem8uaGV5ZUB3ZWdyb3VwLmJlIiwiZXhwIjoxNTUxOTUzNjc4fQ.1p-NvMiT6N1OBu-fBA1l_HDPvQWwTyl9YkwIIFSlO2A"
        }
        request, response = app.test_client.post(
            "/v1/api/allowed", json=body, headers=headers
        )
        resp = response.json
        self.assertEqual(response.status, 401)
        self.assertEqual(resp.get("reasons")[0], "Auth required.")

    def test_allowed_auth_valid_token(self):
        body = {"email": "kenzo.heye@weaids2.be", "password": "123456789abcdef"}
        headers = {"Content-Type": DEFAULT_TYPE, "Accept": DEFAULT_TYPE}
        resp = requests.post(WG_BE_PHOENIX_AUT + "/auth", json=body, headers=headers)
        resp = resp.json()
        a_token = resp.get("access_token", None)
        self.assertIsNotNone(a_token)

        body = {
            "URI": "http://localhost:5002/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        headers = {"authorization": "Bearer " + a_token}
        request, response = app.test_client.post(
            "/v1/api/allowed", json=body, headers=headers
        )
        resp = response.json
        self.assertEqual(response.status, 200)
        self.assertTrue(resp.get("allowed"))

    def test_allowed_auth_valid_token_wrong_role(self):
        body = {"email": "kenzoheye@gmail.com", "password": "wegroupies"}
        headers = {"Content-Type": DEFAULT_TYPE, "Accept": DEFAULT_TYPE}
        resp = requests.post(WG_BE_PHOENIX_AUT + "/auth", json=body, headers=headers)
        resp = resp.json()
        a_token = resp.get("access_token", None)
        self.assertIsNotNone(a_token)

        body = {
            "URI": "http://localhost:5002/",
            "method": "GET",
            "ip": "127.0.0.1:42101",
        }
        headers = {"authorization": "Bearer " + a_token}
        request, response = app.test_client.post(
            "/v1/api/allowed", json=body, headers=headers
        )
        resp = response.json
        self.assertEqual(response.status, 403)
        self.assertEqual(
            resp.get("errors")[0].get("detail"),
            "User does not have the correct access rights",
        )


def clog(text):
    print("======================")
    print(text)
    print("======================")


# run tests
if __name__ == "__main__":
    unittest.main()
