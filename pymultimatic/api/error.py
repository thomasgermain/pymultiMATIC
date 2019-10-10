"""Errors coming from the API."""
from typing import Optional, Any

from requests import Response

import attr


@attr.s
class ApiError(Exception):
    """This exception is thrown when a communication error occurs with the
    vaillant API."""

    message = attr.ib(type=str)
    response = attr.ib(type=Optional[Response])
    payload = attr.ib(type=Any, default=None)
