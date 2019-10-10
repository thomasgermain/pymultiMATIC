"""Test for quick mode."""
import unittest

from pymultimatic.model import QuickModes


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
