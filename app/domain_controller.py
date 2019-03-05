# CODEX XXXXX
#
# X1 = admin
#
#
#
#
#
#
#

SCOPES = {
    "wg-be-carquotes": {
        ("GET", "/openapi/spec.json"): ["admin", "broker", "superbroker", "anonymous"],
        ("POST", "/openapi/spec.json"): ["admin", "broker", "superbroker", "anonymous"],
    }
}

_IN_PROGRESS_API = {
    "models": {
        "car": {"manufacturer": "str", "model": "str", "TODO": "TODO"},
        "driver": {"firsname": "str", "lastname": "str", "TODO": "TODO"},
    },
    "resources": {
        "TEMPLATE": {},
        "_internal_": {},
        "carquotes": {
            "operations": [
                {
                    "scoped": None,
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/create_postal_code",
                    "body": {"postal_code": "int"},
                    "responses": {200: {"id": "str"}, 401: {"TODO"}},
                },
                {
                    "scoped": None,
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/create_car_manual",
                    "body": {"id": "str", "number_plate": "str"},
                    "responses": {200: {"car": "car"}, 401: {"TODO"}},
                },
                {
                    "scoped": None,
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/create_driver_manual",
                    "body": {
                        "id": "str",
                        "firstname": "str",
                        "lastname": "str",
                        "birth": "str",
                        "drivers_birth": "str",
                    },
                    "responses": {200: {"": "driver"}, 401: {"TODO"}},
                },
                {
                    "scoped": None,
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/quote",
                    "body": {"id": "str", "insurance": "str"},
                    "responses": {
                        200: {
                            "insurance_name": "str",
                            "insurance_img": "str",
                            "insurance_url": "str",
                            "quote": "dict",
                        },
                        401: {"TODO"},
                    },
                },
                {
                    "scoped": ["admin"],
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/get_memory",
                    "body": {},
                    "responses": {200: {"memory": "dict"}, 401: {"TODO"}},
                },
                {
                    "scoped": ["admin"],
                    "method": "POST",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/clean_memory",
                    "body": {},
                    "responses": {200: {"status": "str"}, 401: {"TODO"}},
                },
                {
                    "scoped": None,
                    "method": "GET",
                    "description": "TODO",
                    "version": "v1",
                    "path": "/api/v1/carquotes/insurances",
                    "responses": {200: {"insurances": "list"}},
                },
            ]
        },
    },
}


async def auz(email=None, path=None, operation=None):

    try:

        if not email:
            raise Exception("no email!")

        if not path:
            raise Exception("no path!")

        if not operation:
            raise Exception("no operation!")

    except Exception as e:

        return {"error": e}

    return API
