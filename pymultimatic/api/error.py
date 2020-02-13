"""Errors coming from the API."""
from typing import Optional, Any

from aiohttp import ClientResponse

import attr


@attr.s
class ApiError(Exception):
    """This exception is thrown when a communication error occurs with the
    vaillant API."""

    message = attr.ib(type=str)
    response = attr.ib(type=Optional[ClientResponse])
    payload = attr.ib(type=Any, default=None)
