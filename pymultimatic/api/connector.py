"""Low level connector module."""
import logging
from typing import Any, Dict, Optional

import attr
import aiohttp
from yarl import URL

from . import ApiError, urls, defaults

_LOGGER = logging.getLogger('Connector')

HEADER = {'content-type': 'application/json'}


@attr.s
class Connector:
    """This is the low level smart.vaillant.com API connector.

    This is returning the raw JSON from responses or an
    :exc:`~pymultimatic.api.error.ApiError` if something goes wrong
    (basically, when response error code is 4xx or 5xx).

    On the first call, the connector will login automatically (if
    :func:`~login` was not called previously).

    On following calls, the connector will re-use the cookie received from the
    API. If the connector receives an HTTP 401, it will clear the cookie and
    try to re-login before raising an `~pymultimatic.api.error.ApiError`. This
    also means the connector is able to reconnect automatically when cookie is
    outdated.

    Please use :mod:`~pymultimatic.api.urls` in order to generate URL to be
    passed to the connector.64:36

    Args:
        user (str): User to login with.
        password (str): Password associated with the user.
        session: (aiohttp.ClientSession): Session.
        smartphone_id (str): This is required by the API to login.
    """

    _user = attr.ib(type=str)
    _password = attr.ib(type=str, repr=False)
    _session = attr.ib(type=aiohttp.ClientSession)
    _smartphone_id = attr.ib(type=str, default=defaults.SMARTPHONE_ID)

    async def login(self, force: bool = False) -> bool:
        """Log in to the API.

        By default, the ``connector`` will try to re-use cookies

        Args:
            force (bool): If set to ``True``, the connector will clear
                the cookie (if any) and start a new authentication, otherwise
                it will re-use the existing cookie.

        Returns:
            bool: True/False if authentication succeeded or not.
        """
        if force:
            self._clear_cookies()

        if self._get_cookies():
            return True

        token = await self._token()
        await self._authenticate(token)
        return True

    async def is_logged(self) -> bool:
        """Check if the connector is already logged in.

        It relies in the presence of cookies.
        """
        return len(self._get_cookies()) > 0

    async def logout(self) -> bool:
        """Get logged out of the API.

        It first sends a ``logout`` request to the API (it means cookies are
        invalidated), then cookies will be cleared, regardless of the result
        of the ``logout`` request.

        The connector will have to request a new token and ask for cookies if
        a new request is done.


        Raises:
            ApiError: When something went wrong with the API call.
        """
        try:
            if self._get_cookies():
                await self.post(urls.logout())
            return True
        finally:
            self._clear_cookies()

    async def _token(self) -> str:
        params = {
            "smartphoneId": self._smartphone_id,
            "username": self._user,
            "password": self._password
        }

        token_res = await self._session.post(url=urls.new_token(),
                                             json=params,
                                             headers=HEADER)
        if token_res.status == 200:
            json = await token_res.json()
            return str(json['body']['authToken'])
        raise ApiError('Login/password invalid', response=token_res)

    async def _authenticate(self, token: str) -> None:
        params = {
            "smartphoneId": self._smartphone_id,
            "username": self._user,
            "authToken": token
        }

        auth_res = await self._session.post(url=urls.authenticate(),
                                            json=params,
                                            headers=HEADER)

        if auth_res.status > 399:
            raise ApiError("Unable to authenticate", response=auth_res)

    def _get_cookies(self) -> Dict[Any, Any]:
        return self._session.cookie_jar.filter_cookies(URL(urls.base()))

    def _clear_cookies(self) -> None:
        self._session.cookie_jar.clear()

    async def get(self, url: str,
                  payload: Optional[Dict[str, Any]] = None) -> Any:
        """Do a get against vaillant API."""
        return await self.request('get', url, payload)

    async def delete(self, url: str,
                     payload: Optional[Dict[str, Any]] = None) -> Any:
        """Do a delete against vaillant API."""
        return await self.request('delete', url, payload)

    async def put(self, url: str,
                  payload: Optional[Dict[str, Any]] = None) -> Any:
        """Do a put against vaillant API."""
        return await self.request('put', url, payload)

    async def post(self, url: str,
                   payload: Optional[Dict[str, Any]] = None) -> Any:
        """Do a post against vaillant API."""
        return await self.request('post', url, payload)

    async def request(self, method: str, url: str,
                      payload: Optional[Dict[str, Any]] = None) -> Any:
        """Do a request against vaillant API."""
        async with self._session.request(
                method,
                url,
                json=payload,
                headers=HEADER
        ) as resp:
            if resp.status == 401:
                await self.login(True)
                return await self.request(method, url, payload)

            if resp.status > 399:
                # fetch json response so it's available later on
                await resp.json(content_type=None)
                raise ApiError('Cannot ' + method + ' ' + url, response=resp,
                               payload=payload)

            return await resp.json(content_type=None)
