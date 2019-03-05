from __future__ import absolute_import

import logging
import sys

log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "red",
    "ERROR": "bold_red",
    "CRITICAL": "bg_red",
}

LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        "sanic.root": {"level": "DEBUG", "handlers": ["console"]},
        "sanic.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": True,
            "qualname": "sanic.error",
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["access_console"],
            "propagate": True,
            "qualname": "sanic.access",
        },
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stderr,
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": sys.stdout,
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(cyan)s(%(module)s-%(funcName)s:%(lineno)d) %(bold_white)s>>%(reset)s %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "colorlog.ColoredFormatter",
        },
        "access": {
            "format": "%(asctime)s %(green)sREQUEST%(reset)s -(%(name)s)[%(levelname)s][%(host)s]: "
            + "%(bold_green)s%(request)s%(reset)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "colorlog.ColoredFormatter",
        },
    },
)

logger = logging.getLogger("sanic.root")
