from unittest import mock

import pytest
from aioresponses import aioresponses

from pymultimatic.api import ApiError, Connector, urls


@pytest.mark.asyncio
async def test_login_success(connector: Connector, resp: aioresponses) -> None:
    assert await connector.login()
    assert await connector.is_logged()
    assert await connector.login()


@pytest.mark.asyncio
async def test_login_auth_error(connector: Connector, raw_resp: aioresponses) -> None:
    raw_resp.post(urls.new_token(), status=200, payload={"body": {"authToken": "123"}})
    raw_resp.post(urls.authenticate(), status=401)

    try:
        await connector.login()
        raise AssertionError("Error expected")
    except ApiError as err:
        assert urls.authenticate() in err.message

    assert not await connector.is_logged()


@pytest.mark.asyncio
async def test_login_login_error(connector: Connector, raw_resp: aioresponses) -> None:
    raw_resp.post(urls.new_token(), status=401)

    try:
        await connector.login()
        assert False
    except ApiError as err:
        assert urls.new_token() in err.message

    assert not await connector.is_logged()


@pytest.mark.asyncio
async def test_auto_login_before_request(connector: Connector, resp: aioresponses) -> None:
    with mock.patch.object(connector, "login", wraps=connector.login) as mock_login:
        mock_payload = {"test": "test"}
        resp.get(urls.system(serial="123"), status=401)
        resp.get(urls.system(serial="123"), status=200, payload=mock_payload)

        assert not await connector.is_logged()
        payload = await connector.get(urls.system(serial="123"))
        assert payload == mock_payload
        assert await connector.is_logged()
        mock_login.assert_called_once()


@pytest.mark.asyncio
async def test_login_error_before_request(connector: Connector, raw_resp: aioresponses) -> None:
    with mock.patch.object(connector, "login", wraps=connector.login) as mock_login:
        raw_resp.post(urls.new_token(), status=401)
        raw_resp.get(urls.system(serial="123"), status=401)

        try:
            await connector.get(urls.system(serial="123"))
            assert False
        except ApiError as err:
            assert urls.new_token() in err.message
        mock_login.assert_called_once()
        assert not await connector.is_logged()


@pytest.mark.asyncio
async def test_delete(connector: Connector, resp: aioresponses) -> None:
    url = urls.facilities_list(serial="123")

    resp.delete(url=url, status=200)
    await connector.delete(url)


@pytest.mark.asyncio
async def test_put(connector: Connector, resp: aioresponses) -> None:
    url = urls.facilities_list(serial="123")

    resp.put(url=url, status=200)
    await connector.put(url)


@pytest.mark.asyncio
async def test_get(connector: Connector, resp: aioresponses) -> None:
    url = urls.facilities_list(serial="123")

    resp.get(url=url, status=200)
    await connector.get(url)


@pytest.mark.asyncio
async def test_post(connector: Connector, resp: aioresponses) -> None:
    url = urls.facilities_list(serial="123")

    resp.post(url=url, status=200)
    await connector.post(url)
