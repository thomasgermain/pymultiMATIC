import json
import unittest
from datetime import date, timedelta
from typing import Any

from responses import mock as responses  # type: ignore

from tests import testutil
from pymultimatic.api import urls, payloads, ApiError
from pymultimatic.model import OperatingModes, QuickModes, QuickVeto, \
    constants
from pymultimatic.systemmanager import SystemManager


class SystemManagerTest(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = SystemManager('user', 'pass', 'pymultimatic',
                                     testutil.temp_path())

    @responses.activate
    def test_login_ok(self) -> None:
        testutil.mock_full_auth_success()
        self.assertTrue(self.manager.login())

    @responses.activate
    def test_system(self) -> None:
        serial = testutil.mock_full_auth_success()

        with open(testutil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(testutil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(testutil.path('files/responses/systemcontrol'), 'r') as file:
            system_data = json.loads(file.read())

        with open(testutil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        self._mock_urls(hvacstate_data, livereport_data, rooms_data, serial,
                        system_data)

        system = self.manager.get_system()

        self.assertIsNotNone(system)

        self.assertEqual(2, len(system.zones))
        self.assertEqual(4, len(system.rooms))

    @responses.activate
    def test_get_hot_water(self) -> None:
        serial = testutil.mock_full_auth_success()

        with open(testutil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(testutil.path('files/responses/hotwater'), 'r') as file:
            raw_hotwater = json.loads(file.read())

        responses.add(responses.GET, urls.hot_water('Control_DHW')
                      .format(serial_number=serial), json=raw_hotwater,
                      status=200)

        responses.add(responses.GET, urls.live_report()
                      .format(serial_number=serial), json=livereport_data,
                      status=200)

        hot_water = self.manager.get_hot_water('Control_DHW')

        self.assertIsNotNone(hot_water)

        self.assertEqual(urls.live_report().format(serial_number=serial),
                         responses.calls[-1].request.url)
        self.assertEqual(urls.hot_water('Control_DHW')
                         .format(serial_number=serial),
                         responses.calls[-2].request.url)

    @responses.activate
    def test_set_hot_water_setpoint_temperature(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.hot_water_temperature_setpoint('id')
        payload = payloads.hotwater_temperature_setpoint(60.0)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_hot_water_setpoint_temperature('id', 60)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_hot_water_setpoint_temperature_number_to_round(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.hot_water_temperature_setpoint('id')
        payload = payloads.hotwater_temperature_setpoint(60.5)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_hot_water_setpoint_temperature('id', 60.4)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_quick_mode_no_current_quick_mode(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.system_quickmode()
        payload = payloads.quickmode(QuickModes.VENTILATION_BOOST.name)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_quick_mode(QuickModes.VENTILATION_BOOST)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_logout(self) -> None:
        testutil.mock_logout()
        self.manager.logout()

        self.assertEqual(urls.logout(), responses.calls[-1].request.url)

    @responses.activate
    def test_set_quick_veto_room(self) -> None:
        serial_number = testutil.mock_full_auth_success()
        url = urls.room_quick_veto('1').format(serial_number=serial_number)

        quick_veto = QuickVeto(100, 25)
        responses.add(responses.PUT, url, status=200)

        self.manager.set_room_quick_veto('1', quick_veto)
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_hot_water_operation_mode_wrong_mode(self) -> None:
        self.manager.\
            set_hot_water_operating_mode('hotwater', OperatingModes.NIGHT)

    @responses.activate
    def test_set_hot_water_operation_mode_heating_mode(self) -> None:
        serial_number = testutil.mock_full_auth_success()

        url = urls.hot_water_operation_mode('hotwater')\
            .format(serial_number=serial_number)

        responses.add(responses.PUT, url, status=200)
        self.manager.set_hot_water_operating_mode('hotwater',
                                                  OperatingModes.ON)
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_set_quick_veto_zone(self) -> None:
        serial_number = testutil.mock_full_auth_success()
        url = urls.zone_quick_veto("Zone1").format(serial_number=serial_number)

        quick_veto = QuickVeto(100, 25)
        responses.add(responses.PUT, url, status=200)

        self.manager.set_zone_quick_veto('Zone1', quick_veto)
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_set_room_operation_mode_heating_mode(self) -> None:
        serial_number = testutil.mock_full_auth_success()

        url = urls.room_operation_mode('1').format(serial_number=serial_number)

        responses.add(responses.PUT, url, status=200)
        self.manager.set_room_operating_mode('1', OperatingModes.AUTO)
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_room_operation_mode_no_new_mode(self) -> None:
        self.manager.set_room_operating_mode('1', None)

    def test_set_room_operation_mode_wrong_mode(self) -> None:
        self.manager.set_room_operating_mode('1', OperatingModes.NIGHT)

    @responses.activate
    def test_set_zone_operation_mode_heating_mode(self) -> None:
        serial_number = testutil.mock_full_auth_success()

        url = urls.zone_heating_mode('Zone1')\
            .format(serial_number=serial_number)

        responses.add(responses.PUT, url, status=200)
        self.manager.set_zone_operation_mode('Zone1', OperatingModes.AUTO)
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_zone_operation_mode_no_new_mode(self) -> None:
        self.manager.set_zone_operation_mode('Zone1', None)

    def test_set_zone_operation_mode_no_zone(self) -> None:
        self.manager.set_zone_operation_mode(None, OperatingModes.MANUAL)

    def test_set_zone_operation_mode_wrong_mode(self) -> None:
        self.manager.set_zone_operation_mode('Zone1', OperatingModes.ON)

    @responses.activate
    def test_get_room(self) -> None:
        serial = testutil.mock_full_auth_success()

        with open(testutil.path('files/responses/room'), 'r') as file:
            raw_rooms = json.loads(file.read())

        responses.add(responses.GET, urls.room('1')
                      .format(serial_number=serial), json=raw_rooms,
                      status=200)

        new_room = self.manager.get_room('1')
        self.assertIsNotNone(new_room)

    @responses.activate
    def test_get_zone(self) -> None:
        serial = testutil.mock_full_auth_success()

        with open(testutil.path('files/responses/zone'), 'r') as file:
            raw_zone = json.loads(file.read())

        responses.add(responses.GET, urls.zone('Control_ZO2')
                      .format(serial_number=serial), json=raw_zone,
                      status=200)

        new_zone = self.manager.get_zone('Control_ZO2')
        self.assertIsNotNone(new_zone)

    @responses.activate
    def test_get_circulation(self) -> None:
        serial_number = testutil.mock_full_auth_success()

        with open(testutil.path('files/responses/circulation'), 'r') as file:
            raw_circulation = json.loads(file.read())

        responses.add(responses.GET, urls.circulation('id_dhw')
                      .format(serial_number=serial_number),
                      json=raw_circulation, status=200)

        new_circulation = self.manager.get_circulation('id_dhw')
        self.assertIsNotNone(new_circulation)

    @responses.activate
    def test_set_room_setpoint_temperature(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.room_temperature_setpoint('1')
        payload = payloads.room_temperature_setpoint(22.0)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_room_setpoint_temperature('1', 22)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_zone_setpoint_temperature(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.zone_heating_setpoint_temperature('Zone1')
        payload = payloads.zone_temperature_setpoint(25.5)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_zone_setpoint_temperature('Zone1', 25.5)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_zone_setback_temperature(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.zone_heating_setback_temperature('Zone1')
        payload = payloads.zone_temperature_setback(18.0)

        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)

        self.manager.set_zone_setback_temperature('Zone1', 18)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_holiday_mode(self) -> None:
        serial = testutil.mock_full_auth_success()

        tomorrow = date.today() + timedelta(days=1)
        after_tomorrow = tomorrow + timedelta(days=1)

        url = urls.system_holiday_mode()
        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)
        payload = payloads.holiday_mode(True, tomorrow, after_tomorrow, 15)

        self.manager.set_holiday_mode(tomorrow, after_tomorrow, 15)
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_remove_holiday_mode(self) -> None:
        serial = testutil.mock_full_auth_success()

        yesterday = date.today() - timedelta(days=1)
        before_yesterday = yesterday - timedelta(days=1)

        url = urls.system_holiday_mode()
        responses.add(responses.PUT, url.format(serial_number=serial),
                      status=200)
        payload = payloads.holiday_mode(False, before_yesterday, yesterday,
                                        constants.FROST_PROTECTION_TEMP)

        self.manager.remove_holiday_mode()
        self.assertEqual(json.dumps(payload),
                         responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_remove_zone_quick_veto(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.zone_quick_veto('id').format(serial_number=serial)
        responses.add(responses.DELETE, url, status=200)

        self.manager.remove_zone_quick_veto('id')
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_remove_room_quick_veto(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.room_quick_veto('1').format(serial_number=serial)
        responses.add(responses.DELETE, url, status=200)

        self.manager.remove_room_quick_veto('1')
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_request_hvac_update(self) -> None:
        serial = testutil.mock_full_auth_success()

        url_update = urls.hvac_update().format(serial_number=serial)
        responses.add(responses.PUT, url_update, status=200)

        with open(testutil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        url_hvac = urls.hvac().format(serial_number=serial)
        responses.add(responses.GET, url_hvac, json=hvacstate_data, status=200)

        self.manager.request_hvac_update()
        self.assertEqual(url_update, responses.calls[-1].request.url)
        self.assertEqual(url_hvac, responses.calls[-2].request.url)

    @responses.activate
    def test_request_hvac_not_sync(self) -> None:
        serial = testutil.mock_full_auth_success()

        url_update = urls.hvac_update().format(serial_number=serial)
        responses.add(responses.PUT, url_update, status=200)

        with open(testutil.path('files/responses/hvacstate_pending'), 'r') \
                as file:
            hvacstate_data = json.loads(file.read())

        url_hvac = urls.hvac().format(serial_number=serial)
        responses.add(responses.GET, url_hvac, json=hvacstate_data, status=200)

        self.manager.request_hvac_update()
        self.assertEqual(url_hvac, responses.calls[-1].request.url)

    @responses.activate
    def test_remove_quick_mode(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.system_quickmode().format(serial_number=serial)
        responses.add(responses.DELETE, url, status=200)

        self.manager.remove_quick_mode()
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_remove_quick_mode_no_active_quick_mode(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.system_quickmode().format(serial_number=serial)
        responses.add(responses.DELETE, url, status=409)

        self.manager.remove_quick_mode()
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_remove_quick_mode_error(self) -> None:
        serial = testutil.mock_full_auth_success()

        url = urls.system_quickmode().format(serial_number=serial)
        responses.add(responses.DELETE, url, status=500)

        try:
            self.manager.remove_quick_mode()
        except ApiError as exc:
            self.assertEqual(500, exc.response.status_code)

        self.assertEqual(url, responses.calls[-1].request.url)

    # pylint: disable=no-self-use,too-many-arguments
    def _mock_urls(self, hvacstate_data: Any, livereport_data: Any,
                   rooms_data: Any, serial: str, system_data: Any) -> None:
        responses.add(responses.GET, urls.live_report()
                      .format(serial_number=serial), json=livereport_data,
                      status=200)
        responses.add(responses.GET, urls.rooms().format(serial_number=serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, urls.system()
                      .format(serial_number=serial), json=system_data,
                      status=200)
        responses.add(responses.GET, urls.hvac().format(serial_number=serial),
                      json=hvacstate_data, status=200)
