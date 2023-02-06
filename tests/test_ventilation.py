import unittest

from pymultimatic.model import OperatingModes, SettingModes
from tests.conftest import _full_day_time_program, _ventilation


class ZoneTest(unittest.TestCase):
    def test_get_active_mode_night(self) -> None:
        ventilation = _ventilation()
        ventilation.operating_mode = OperatingModes.NIGHT
        active_mode = ventilation.active_mode

        self.assertEqual(OperatingModes.NIGHT, active_mode.current)
        self.assertEqual(ventilation.target_low, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_day(self) -> None:
        ventilation = _ventilation()
        ventilation.operating_mode = OperatingModes.DAY
        active_mode = ventilation.active_mode

        self.assertEqual(OperatingModes.DAY, active_mode.current)
        self.assertEqual(ventilation.target_high, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_off(self) -> None:
        ventilation = _ventilation()
        ventilation.operating_mode = OperatingModes.OFF

        active_mode = ventilation.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertEqual(1, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_auto_on(self) -> None:
        ventilation = _ventilation()
        ventilation.operating_mode = OperatingModes.AUTO

        active_mode = ventilation.active_mode

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(3, active_mode.target)
        self.assertEqual(SettingModes.ON, active_mode.sub)

    def test_get_active_mode_auto_off(self) -> None:
        ventilation = _ventilation()
        ventilation.time_program = _full_day_time_program(SettingModes.OFF)
        ventilation.operating_mode = OperatingModes.AUTO

        active_mode = ventilation.active_mode

        self.assertEqual(OperatingModes.AUTO, active_mode.current)
        self.assertEqual(1, active_mode.target)
        self.assertEqual(SettingModes.OFF, active_mode.sub)
