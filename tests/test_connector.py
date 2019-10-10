"""Test for connector."""
import json
import unittest
from unittest.mock import Mock
from responses import mock as responses  # type: ignore

from tests import testutil
from pymultimatic.api import urls, ApiError, ApiConnector


class ConnectorTest(unittest.TestCase):
    """Test class."""

    def setUp(self) -> None:
        """setup."""
        self.connector = ApiConnector('user', 'pass', 'vr900-connector',
                                      testutil.temp_path())

    @responses.activate
    def tearDown(self) -> None:
        """tear down."""
        if self.connector:
            testutil.mock_logout()
            self.connector.logout()

    @responses.activate
    def test_login(self) -> None:
        """Test calls done during login."""
        testutil.mock_full_auth_success()

        self.connector.get(urls.facilities_list())
        self.assertEqual(4, len(responses.calls))
        self.assertEqual(urls.new_token(), responses.calls[0].request.url)
        self.assertEqual(urls.authenticate(), responses.calls[1].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[2].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[3].request.url)

    @responses.activate
    def test_check_login_wrong_not_force(self) -> None:
        """Test login with wrong credentials."""
        responses.add(responses.POST, urls.new_token(), status=401)

        self.assertFalse(self.connector.login())
        self.assertEqual(1, len(responses.calls))
        self.assertEqual(urls.new_token(), responses.calls[0].request.url)

    @responses.activate
    def test_check_login_wrong_force(self) -> None:
        """Test login with wrong credentials."""
        responses.add(responses.POST, urls.new_token(), status=401)

        self.assertFalse(self.connector.login(True))
        self.assertEqual(1, len(responses.calls))
        self.assertEqual(urls.new_token(), responses.calls[0].request.url)

    @responses.activate
    def test_check_login_ok(self) -> None:
        """Test login with correct credentials."""
        testutil.mock_full_auth_success()

        self.assertTrue(self.connector.login())
        self.assertEqual(3, len(responses.calls))
        self.assertTrue(self.connector.login())
        self.assertEqual(3, len(responses.calls))

    @responses.activate
    def test_check_login_ok_force(self) -> None:
        """Test login with correct credentials and force re-authentication."""
        testutil.mock_full_auth_success()

        self.assertTrue(self.connector.login())
        self.assertEqual(3, len(responses.calls))
        self.assertTrue(self.connector.login(True))
        self.assertEqual(6, len(responses.calls))

    @responses.activate
    def test_check_login_unknown_error(self) -> None:
        """Check login with unknown error (like no internet connection)."""
        self.assertFalse(self.connector.login(False))

    @responses.activate
    def test_re_login(self) -> None:
        """Test ensure connector tries to re-login in case of HTTP 401."""
        serial_number = testutil.mock_full_auth_success()

        repeaters_url = urls.repeaters().format(serial_number=serial_number)
        responses.add(responses.GET, repeaters_url, status=401)

        try:
            self.connector.get(urls.repeaters())
            self.fail('Error expected')
        except ApiError as exc:
            self.assertEqual(8, len(responses.calls))
            self.assertEqual(401, exc.response.status_code)
            self.assertEqual(repeaters_url, exc.response.url)
            self.assertEqual(repeaters_url, responses.calls[3].request.url)
            self.assertEqual(repeaters_url, responses.calls[7].request.url)

    @responses.activate
    def test_cookie_failed(self) -> None:
        """Test cannot get cookies."""
        testutil.mock_token_success()

        responses.add(responses.POST, urls.authenticate(), status=401)

        try:
            self.connector.get(urls.facilities_list())
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Cannot get cookies", exc.message)

    @responses.activate
    def test_cookie_failed_exception(self) -> None:
        """Test cannot get cookie, unknown exception."""
        testutil.mock_token_success()

        try:
            self.connector.get(urls.facilities_list())
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Error while getting cookies", exc.message)
            self.assertIsNone(exc.response)

    @responses.activate
    def test_login_wrong_authentication(self) -> None:
        """Test with real response sent from API."""
        with open(testutil.path('files/responses/wrong_token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, urls.new_token(), json=token_data,
                      status=401)

        try:
            self.connector.get(urls.facilities_list())
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Authentication failed", exc.message)

    @responses.activate
    def test_put(self) -> None:
        """Test ensure put is working as expected."""
        serial = testutil.mock_full_auth_success()

        responses.add(responses.PUT, urls.rooms().format(serial_number=serial),
                      json='', status=200)
        self.connector.put(urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('PUT', responses.calls[3].request.method)

    @responses.activate
    def test_post(self) -> None:
        """Test ensure post is working as expected."""
        serial = testutil.mock_full_auth_success()

        responses.add(responses.POST, urls.rooms()
                      .format(serial_number=serial), json='', status=200)
        self.connector.post(urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('POST', responses.calls[3].request.method)

    @responses.activate
    def test_delete(self) -> None:
        """Test ensure delete is working as expected."""
        serial = testutil.mock_full_auth_success()

        responses.add(responses.DELETE, urls.rooms()
                      .format(serial_number=serial), json='', status=200)
        self.connector.delete(urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('DELETE', responses.calls[3].request.method)

    @responses.activate
    def test_cannot_get_serial(self) -> None:
        """Test error while getting serial."""
        testutil.mock_authentication_success()
        testutil.mock_token_success()

        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Cannot get serial number", exc.message)
            self.assertIsNone(exc.response)

    @responses.activate
    def test_cannot_get_serial_bad_request(self) -> None:
        """Test bad request while getting serial."""
        testutil.mock_authentication_success()
        testutil.mock_token_success()

        responses.add(responses.GET, urls.facilities_list(), json='',
                      status=400)

        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Cannot get serial number", exc.message)
            self.assertIsNotNone(exc.response)
            self.assertEqual(400, exc.response.status_code)

    @responses.activate
    def test_logout_failed(self) -> None:
        """Test cannot logout."""
        testutil.mock_full_auth_success()

        try:
            self.connector.logout()
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Error during logout", exc.message)
            self.assertIsNone(self.connector._serial_number)
            self.assertEqual(0, len(self.connector._session.cookies))

    @responses.activate
    def test_call_empty_response_success(self) -> None:
        """Test to ensure the connector returns the response body correctly."""
        serial = testutil.mock_full_auth_success()

        responses.add(responses.GET, urls.rooms().format(serial_number=serial),
                      status=200)

        result = self.connector.get(urls.rooms())
        self.assertEqual(None, result)

    @responses.activate
    def test_call_error(self) -> None:
        """Test error handling is correct on error."""
        serial = testutil.mock_full_auth_success()

        try:
            self.connector.get(urls.rooms())
            self.fail("Error expected")
        except ApiError as exc:
            self.assertEqual("Cannot GET url: " + urls.rooms()
                             .format(serial_number=serial), exc.message)

    @responses.activate
    def test_request_token_error(self) -> None:
        """Test to ensure error handling is correct."""
        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as exc:
            self.assertIsNone(exc.response)
            self.assertEqual('Error during authentication', exc.message)

    @responses.activate
    def test_login_error(self) -> None:
        """Test to ensure error handling is correct."""
        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as exc:
            self.assertIsNone(exc.response)
            self.assertEqual('Error during authentication', exc.message)

    @responses.activate
    def test_login_catch_exception(self) -> None:
        """Test to ensure error handling is correct."""
        testutil.mock_full_auth_success()

        error = Mock(side_effect=Exception('Test exception'))
        self.connector._create_or_load_session = error  # type: ignore

        self.connector._session.cookies = None

        try:
            self.connector.get('')
        except ApiError as exc:
            self.assertIsNone(exc.response)
            self.assertEqual('Error during login', exc.message)

    @responses.activate
    def test_login_once(self) -> None:
        """Test to ensure login only occurs once."""
        testutil.mock_full_auth_success()

        self.connector.get(urls.facilities_list())
        self.connector.get(urls.facilities_list())
        self.assertEqual(5, len(responses.calls))
        self.assertEqual(urls.new_token(), responses.calls[0].request.url)
        self.assertEqual(urls.authenticate(), responses.calls[1].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[2].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[3].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[4].request.url)

    @responses.activate
    def test_login_loaded_session(self) -> None:
        """Test to ensure no authentication if cookies are already there."""

        testutil.mock_full_auth_success()
        self.connector = ApiConnector('user', 'pass', 'vr900-connector',
                                      testutil.path('./files/session'))

        # Do nothing on clear session, otherwise it will delete files
        # in tests/files/session
        self.connector._clear_session = Mock()  # type: ignore

        self.connector.get(urls.facilities_list())

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(urls.facilities_list(),
                         responses.calls[0].request.url)

    @responses.activate
    def test_login_loaded_session_no_serial(self) -> None:
        """Test to ensure serial is loaded or find from the API."""
        testutil.mock_full_auth_success()
        self.connector = ApiConnector('user', 'pass', 'vr900-connector',
                                      testutil.path('./files/session'))

        # Do nothing on clear session, otherwise it will delete files
        # in tests/files/session
        self.connector._clear_session = Mock()  # type: ignore
        self.connector._serial_number = None

        self.connector.get(urls.facilities_list())

        self.assertEqual(2, len(responses.calls))
        self.assertEqual(urls.facilities_list(),
                         responses.calls[0].request.url)
        self.assertEqual(urls.facilities_list(),
                         responses.calls[1].request.url)
