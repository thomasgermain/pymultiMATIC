"""Test for rooms."""
import unittest

from pymultimatic.model import OperatingModes, Room
from tests.conftest import _room


class RoomTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_manual(self) -> None:
        """Test active mode manual."""
        room = _room()
        room.operating_mode = OperatingModes.MANUAL
        room.target_high = 5

        active_mode = room.active_mode

        self.assertEqual(OperatingModes.MANUAL, active_mode.current)
        self.assertEqual(5, active_mode.target)
        self.assertIsNone(active_mode.sub)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        room = _room()
        room.operating_mode = OperatingModes.OFF

        active_mode = room.active_mode

        self.assertEqual(OperatingModes.OFF, active_mode.current)
        self.assertEqual(Room.MIN_TARGET_TEMP, active_mode.target)
        self.assertIsNone(active_mode.sub)
