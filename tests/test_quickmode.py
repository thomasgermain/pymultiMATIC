"""Test for quick mode."""
import unittest

from pymultimatic.model import QuickModes, Zone, Room, Circulation, HotWater


class QuickModeTest(unittest.TestCase):
    """Test class."""

    def test_for_zone(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_zone()
        self.assertEqual(6, len(values))

    def test_for_room(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_room()
        self.assertEqual(2, len(values))

    def test_for_dhw(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_dhw()
        self.assertEqual(4, len(values))

    def test_is_for(self) -> None:
        for mode in QuickModes._VALUES.values():
            self.assertEqual(mode.for_zone, mode.is_for(Zone()))
            self.assertEqual(mode.for_room, mode.is_for(Room()))
            self.assertEqual(mode.for_dhw, mode.is_for(Circulation()))
            self.assertEqual(mode.for_dhw, mode.is_for(HotWater()))
