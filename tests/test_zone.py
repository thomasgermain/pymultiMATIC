import unittest

from pymultimatic.model import Zone, OperatingModes


class ZoneTest(unittest.TestCase):

    def test_get_active_mode_night(self) -> None:
        zone = Zone('id', 'Test', None, 10.0, 7.0, OperatingModes.NIGHT, None,
                    6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.NIGHT, active_mode.current_mode)
        self.assertEqual(6.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_day(self) -> None:
        zone = Zone('id', 'Test', None, 10.0, 7.0, OperatingModes.DAY, None,
                    6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.DAY, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self) -> None:
        zone = Zone('id', 'Test', None, 10.0, 7.0, OperatingModes.OFF, None,
                    6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current_mode)
        self.assertEqual(Zone.MIN_TARGET_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
