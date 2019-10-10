"""Tests for circulation."""
import unittest

from tests import testutil
from pymultimatic.model import Circulation, OperatingModes


class CirculationTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_on(self) -> None:
        """Get active mode when operation mode is ON."""
        circulation = Circulation('id', 'Test',
                                  testutil.default_time_program(),
                                  OperatingModes.ON)

        active_mode = circulation.active_mode

        self.assertEqual(OperatingModes.ON, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
