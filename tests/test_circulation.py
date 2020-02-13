"""Tests for circulation."""
import unittest

from pymultimatic.model import OperatingModes
from tests.conftest import _circulation


class CirculationTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_on(self) -> None:
        """Get active mode when operation mode is ON."""
        circulation = _circulation()
        circulation.operating_mode = OperatingModes.ON

        active_mode = circulation.active_mode

        self.assertEqual(OperatingModes.ON, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_off(self) -> None:
        """Get active mode when operation mode is OFF."""
        circulation = _circulation()
        circulation.operating_mode = OperatingModes.OFF

        active_mode = circulation.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertIsNone(active_mode.target)
        self.assertIsNone(active_mode.sub)
