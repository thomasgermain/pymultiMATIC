"""Test for quick mode."""
import unittest

from pymultimatic.model import Circulation, HotWater, QuickModes, Room, Ventilation, Zone


class QuickModeTest(unittest.TestCase):
    """Test class."""

    def test_for_zone(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_zone()
        self.assertEqual(7, len(values))

    def test_for_room(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_room()
        self.assertEqual(2, len(values))

    def test_for_dhw(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_dhw()
        self.assertEqual(5, len(values))

    def test_for_ventilation(self) -> None:
        """Test get quick mode for zone."""
        values = QuickModes.for_ventilation()
        self.assertEqual(5, len(values))

    def test_is_for(self) -> None:
        for mode in QuickModes._VALUES.values():
            self.assertEqual(mode.for_zone, mode.is_for(Zone()), mode)
            self.assertEqual(mode.for_room, mode.is_for(Room()), mode)
            self.assertEqual(mode.for_dhw, mode.is_for(Circulation()), mode)
            self.assertEqual(mode.for_dhw, mode.is_for(HotWater()), mode)
            self.assertEqual(mode.for_ventilation, mode.is_for(Ventilation()), mode)
