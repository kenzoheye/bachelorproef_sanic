from __future__ import absolute_import
from logger import logger


class AuthorizationRequest(object):

    host = None
    method = None
    uri = None
    ip = None
    authorization_header = None
    is_system_token = False

    def __init__(
        self, host, method, uri, ip, authorization_header=None, *args, **kwargs
    ):
        if args:
            logger.debug(f"got to many arguments for args: {args}")
        if kwargs:
            logger.debug(f"got to many arguments for kwargs: {kwargs}")

        self.host = host
        self.method = method
        self.uri = uri
        self.ip = ip
        self.authorization_header = authorization_header

        if authorization_header and authorization_header.startswith("WG-SYSTEM-TOKEN="):
            self.is_system_token = True

    def __repr__(self):
        if self.authorization_header:
            return f"<AuthorizationRequest {self.host} {self.method} {self.uri} {self.authorization_header[0:30]}... from ip: {self.ip}>"
        else:
            return f"<AuthorizationRequest {self.host} {self.method} {self.uri} from {self.ip}>"
