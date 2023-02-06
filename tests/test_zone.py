import unittest

from pymultimatic.model import ActiveFunction, OperatingModes, SettingModes, Zone, ZoneCooling
from tests.conftest import _full_day_time_program, _zone, _zone_cooling


class ZoneTest(unittest.TestCase):
    def test_get_active_mode_night(self) -> None:
        zone = _zone()
        zone.heating.operating_mode = OperatingModes.NIGHT
        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.NIGHT, active_mode.current)
        self.assertEqual(zone.heating.target_low, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_day(self) -> None:
        zone = _zone()
        zone.heating.operating_mode = OperatingModes.DAY
        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.DAY, active_mode.current)
        self.assertEqual(zone.heating.target_high, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_off(self) -> None:
        zone = _zone()
        zone.heating.operating_mode = OperatingModes.OFF

        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertEqual(Zone.MIN_TARGET_HEATING_TEMP, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_cooling_active_mode_auto(self) -> None:
        cooling = ZoneCooling()
        cooling.operating_mode = OperatingModes.AUTO
        cooling.time_program = _full_day_time_program()

        active_mode = cooling.active_mode
        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.ON, active_mode.sub)

    def test_cooling_active_mode_auto_off(self) -> None:
        cooling = ZoneCooling()
        cooling.operating_mode = OperatingModes.AUTO
        cooling.time_program = _full_day_time_program(mode=SettingModes.OFF)

        active_mode = cooling.active_mode
        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(SettingModes.OFF, active_mode.sub)

    def test_cooling_active_mode_on(self) -> None:
        cooling = ZoneCooling()
        cooling.operating_mode = OperatingModes.ON
        cooling.time_program = _full_day_time_program()

        active_mode = cooling.active_mode
        self.assertEqual(OperatingModes.ON, active_mode.current)
        self.assertIsNone(active_mode.sub)

    def test_cooling_active_mode_off(self) -> None:
        cooling = ZoneCooling()
        cooling.operating_mode = OperatingModes.OFF
        cooling.time_program = _full_day_time_program()

        active_mode = cooling.active_mode
        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_cooling_auto(self) -> None:
        zone = _zone_cooling()
        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(zone.cooling.target_high, active_mode.target)
        self.assertEqual(SettingModes.ON, active_mode.sub)

    def test_get_active_mode_standby_cooling(self) -> None:
        zone = _zone_cooling()
        zone.active_function = ActiveFunction.STANDBY
        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(zone.cooling.target_high, active_mode.target)
        self.assertEqual(SettingModes.ON, active_mode.sub)

    def test_get_active_mode_standby_heating(self) -> None:
        zone = _zone()
        zone.active_function = ActiveFunction.STANDBY
        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(zone.heating.target_high, active_mode.target)
        self.assertEqual(SettingModes.DAY, active_mode.sub)
