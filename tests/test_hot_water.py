"""Test for hot water."""
import unittest

from pymultimatic.model import OperatingModes, constants
from tests.conftest import _hotwater


class HotWaterTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_on(self) -> None:
        """Test active mode on."""
        hot_water = _hotwater()
        hot_water.operating_mode = OperatingModes.ON

        active_mode = hot_water.active_mode

        self.assertEqual(OperatingModes.ON, active_mode.current)
        self.assertEqual(hot_water.target_high, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        hot_water = _hotwater()
        hot_water.operating_mode = OperatingModes.OFF

        active_mode = hot_water.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertEqual(constants.FROST_PROTECTION_TEMP, active_mode.target)
        self.assertIsNone(active_mode.sub)
