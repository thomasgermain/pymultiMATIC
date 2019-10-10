"""Test for rooms."""
import unittest

from pymultimatic.model import Room, OperatingModes


class RoomTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_manual(self) -> None:
        """Test active mode manual."""
        room = Room('1', 'Test', None, 5.0, 7.0, OperatingModes.MANUAL, None,
                    True, False, [])

        active_mode = room.active_mode

        self.assertEqual(OperatingModes.MANUAL, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        hot_water = Room('1', 'Test', None, 5.0, 7.0, OperatingModes.OFF, None,
                         True, False, [])

        active_mode = hot_water.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current_mode)
        self.assertEqual(Room.MIN_TARGET_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
