"""Test for quick veto."""
import unittest

from pymultimatic.model import QuickVeto


class QuickVetoTest(unittest.TestCase):
    """Test class."""

    def test_wrong_quick_veto(self) -> None:
        """Test duration no correct."""
        self.assertRaises(ValueError, QuickVeto, 800000, 15)

    def test_quick_veto(self) -> None:
        """Test correct quick veto."""
        quickveto = QuickVeto(600, 15)
        self.assertEqual(600, quickveto.remaining_duration)
        self.assertEqual(15, quickveto.target_temperature)
