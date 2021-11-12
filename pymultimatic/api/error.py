"""Errors coming from the API."""
from typing import Any, Optional

import attr


@attr.s
class ApiError(Exception):
    """This exception is thrown when a communication error occurs with the
    vaillant API."""

    message = attr.ib(type=str)
    response = attr.ib(type=Optional[str])
    status = attr.ib(type=int)
    payload = attr.ib(type=Any, default=None)

    def __str__(self) -> str:
        return (
            f"{self.message}, status: {self.status}, response: {self.response},"
            f"payload: {self.payload}"
        )


@attr.s
class WrongResponseError(ApiError):
    """This exception is thrown when the response coming from the API is wrong."""

    status = attr.ib(default=200, type=int)
