"""Test for hot water."""
import unittest

from tests import testutil
from pymultimatic.model import HotWater, OperatingModes, constants


class HotWaterTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_on(self) -> None:
        """Test active mode on."""
        hot_water = HotWater('id', 'Test', testutil.default_time_program(),
                             5.0, 7.0, OperatingModes.ON)

        active_mode = hot_water.active_mode

        self.assertEqual(OperatingModes.ON, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        hot_water = HotWater('id', 'Test', testutil.default_time_program(),
                             5.0, 7.0, OperatingModes.OFF)

        active_mode = hot_water.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current_mode)
        self.assertEqual(constants.FROST_PROTECTION_TEMP,
                         active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
