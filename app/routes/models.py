from __future__ import absolute_import
from sanic_openapi import doc


class AllowedConsumes:
    uri = doc.String(
        name="uri", description="the uri", example="/v1/api/users", required=True
    )
    method = doc.String(
        name="method", description="the method", example="GET", required=True
    )
    ip = doc.String(
        name="ip", description="the ip", example="78.21.146.62", required=True
    )
    host = doc.String(
        name="host", description="the host", example="wg-be-phoenix-main", required=True
    )
